import os
import dotenv
import json
import mysql.connector
import shellescape

SSH_DIR="/opt/ssh"
EXPECT_SSH="/usr/local/nagios/libexec/shell/remote_ssh_cmd.expect"

class Env:
    __instance = None
    @classmethod
    def get(cls, key):
        cls.__reload()
        return os.getenv(key)
    
    @classmethod
    def __reload(cls):
        if cls.__instance is None:
            dotenv.load_dotenv('/opt/.env')
            cls.__instance = True
        return None

class RemoteCmd:
    @classmethod
    def __prepare(cls, host_name, host_address):
        # read JSON file
        try:
            json_file = "{!s}/{!s}.json".format(SSH_DIR,host_name)
            json_fd = open(json_file, 'r')
        except Exception as e:
            raise Exception("JSON file cannot read {!s}, exception {!s}".format(json_file,e))
            
        # read data
        try:
            data = json.loads(json_fd.read())
        except Exception as e:
            raise Exception("JSON parse error, exception {!s}".format(e))
        
        ssh_user = data.get('user', '')
        ssh_pswd = data.get('password', '')
        ssh_key = data.get('key', '')
        key_file = "{!s}/{!s}".format(SSH_DIR,ssh_key)
        
        if len(ssh_user)==0:
            raise Exception("ssh login user not found in JSON")
        if len(ssh_key) and os.path.isfile(key_file) == False:
            raise Exception("ssh key not found at {!s}".format(key_file))
        
        if len(ssh_key) == 0:
            ssh_cmd = "ssh {!s}@{!s}".format(ssh_user, host_address)
        else:
            ssh_cmd = "ssh -i {!s} {!s}@{!s}".format(key_file, ssh_user, host_address)
        
        return {
            'ssh_cmd': ssh_cmd,
            'ssh_pswd': ssh_pswd,
        }
        
    @classmethod
    def commit(cls, host_name, host_address, remote_cmd):
        # prepare
        params = cls.__prepare(host_name, host_address)
            # raise error if exception found
        cmd_fd = os.popen('{!s} {!s} {!s} {!s}'.format(
            shellescape.quote(EXPECT_SSH),
            shellescape.quote(params['ssh_cmd']),
            shellescape.quote(params['ssh_pswd']),
            shellescape.quote(remote_cmd)
        ))
        return cmd_fd.read()
        
        

class BigObject:
    __name = 'default'
    __instance = {}
    __config = {}
    
    @classmethod
    def connect(cls, host, port, db, name='default'):
        # connection not initialized
        if name not in cls.__config:
            cls.__config[name] = {'host':host, 'port':port, 'db':db}
            cls.__setupClient(name)
             
        # reconnect if connection initialized, but not alive
        if cls.__alive(name) == False:
            # reconnect
            cls.__setupClient(name)
            
        return cls
    # :def connect
    
    @classmethod
    def __setupClient(cls, name):
        params = cls.__config[name]
        cls.__instance[name] = mysql.connector.connect( 
            host=params['host'], 
            port=params['port'], 
            database=params['db'], 
            connection_timeout=600 
        )
    # :def __setupClient
    
    @classmethod
    def __alive(cls, name):
        bo_client = cls.__instance[name]
        try:
            bo_client.ping()
            return True
        except Exception as e:
            return False
    # :def ping
    
    @classmethod
    def query(cls, sql, *args, **kwargs):
        if cls.__alive(cls.__name) == False:
            cls.__setupClient(cls.__name)
        
        bo_client = cls.__instance[cls.__name]
        bo_cursor = bo_client.cursor(dictionary=True, buffered=True)
        bo_cursor.execute(sql, *args, **kwargs)
        return bo_cursor
    # :def query
