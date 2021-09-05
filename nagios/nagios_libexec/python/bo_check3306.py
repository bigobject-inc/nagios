import sys
import click
from kit import BigObject
from kit import Fernet

# python3 ... HOST PORT
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

@click.command(help='check BO license time')
@click.argument('host')
@click.argument('port')
@click.argument('db')
@click.option('--user', default='root')
@click.option('--password', default='')
def main(host, port, db, user, password):
    """ Verify BO liveness via sql connection query """
    # decipher password
    if len(password) != 0:
        fernet = Fernet.getOptEnv()
        password = fernet.decrypt(password)

    # setup connection
    bo_client = BigObject.connect(host, port, db, user, password)
    result = bo_client.query("SELECT 1 as result")

    # get result and verify
    row = result.fetchone()
    if row.get('result',0) != 1:
        print('SELECT 1 error')
        sys.exit(NAGIOS_WARNING)

    print('OK')
    sys.exit(NAGIOS_OK)

# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
