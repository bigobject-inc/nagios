import os
import dotenv
import mysql.connector

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
