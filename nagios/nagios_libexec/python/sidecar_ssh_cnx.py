import click
import os
import json
from kit import Fernet
SSH_DIR="/opt/ssh/"

@click.command(help="create ssh connection template")
def main():
    """ output json for ssh connection """

    # collect required information for ssh connection
    host_name = click.prompt('Host name(the same in nagios configuration)', type=str)
        # host_name
    ssh_user = click.prompt('Username(login as which remote user)', type=str)
        # user

    need_pswd = click.confirm('Need login password?')
    is_encrypted = click.confirm('Would you like password encrypted?') if need_pswd else False
    if need_pswd:
        # ask password if needed
        ssh_pswd = click.prompt('Password', type=str)

    if need_pswd and is_encrypted:
        # encrypt password if needed
        fernet = Fernet.getOptEnv()
        ssh_pswd = fernet.encrypt(ssh_pswd)


    # ssh key setup
    key_file = click.prompt('key file(eg. xxx.pem) under /opt/ssh') \
        if click.confirm('Need ssh key?') \
        else ''

    key_path = "{!s}{!s}".format(SSH_DIR, key_file) if len(key_file) else None
    while key_path is not None :
        if os.path.isfile(key_path) == False:
            click.confirm("key not found, please save key at {!s}".format(key_path), abort=True)
        else:
            break

    # create json file for connection
    cnx_path = "{!s}{!s}.json".format(SSH_DIR,host_name)
    cnx_param = {
        'user': ssh_user,
        'password': ssh_pswd,
        'key': key_file,
        'is_encrypted': is_encrypted
    }
    fd = open(cnx_path, 'w', encoding='utf-8')
    fd.write(json.dumps(cnx_param))
    fd.close()
        # write json file
    os.popen("chown nagios:nagios {!s}".format(cnx_path))
        # modify owner

    # modify key file owner, mod
    if key_path is not None:
        os.popen("chown nagios:nagios {!s}".format(key_path))
        os.popen("chmod 0400 {!s}".format(key_path))

    click.echo("=== Everything is OK ===")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
