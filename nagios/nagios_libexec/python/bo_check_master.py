import sys
import click
from kit import BigObject
from kit import Fernet

# python3 ... MASTER_HOST MASTER_PORT MASTER_DB CLUSTER_NUM
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

@click.command(help='check BO license time')
@click.argument('host')
@click.argument('port')
@click.argument('db')
@click.argument('alert_num', type=int)
@click.option('--user', default='root')
@click.option('--password', default='')
def main(host, port, db, alert_num, user, password):
    """ verify connected BO in master """
    # decipher password
    if len(password) != 0:
        fernet = Fernet.getOptEnv()
        password = fernet.decrypt(password)

    # setup connection and query
    bo_client = BigObject.connect(host, port, db, user, password)
    cursor = bo_client.query("remote SELECT 1 as result")
    rows = cursor.fetchall()

    # get result from all remote host
    if len(rows) == 0:
        print("no remote cluster found")
        sys.exit(NAGIOS_WARNING)

    # verify query result with desired value
    qr_cluster_num = sum([ item['result'] for item in rows ])
    print("{!s} found, alert if < {!s}".format(qr_cluster_num, alert_num))
    if qr_cluster_num < alert_num:
        sys.exit(NAGIOS_WARNING)

    sys.exit(NAGIOS_OK)

# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
