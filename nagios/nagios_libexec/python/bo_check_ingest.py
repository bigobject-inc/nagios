import sys
import click
from kit import BigObject
from kit import Fernet

# python3 ... HOST PORT DB TABLE SCHEME THRESHOLD
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

@click.command(help='check number of rows in BO table against a threshold')
@click.argument('host')
@click.argument('port')
@click.argument('db')
@click.argument('table')
@click.argument('scheme', type=click.Choice(['above','below']))
@click.argument('threshold', type=int)
@click.option('--user', default='root')
@click.option('--password', default='')
def main(host, port, db, table, scheme, threshold, user, password):
    """ check numbers of rows in a table against a threshold """
    # decipher password
    if len(password) != 0:
        fernet = Fernet.getOptEnv()
        password = fernet.decrypt(password)

    # setup connection
    bo_client = BigObject.connect(host, port, db, user, password)

    # Part I. check existence on table
    cursor = bo_client.query("SELECT COUNT(*) as result from (show tables) where Tables_in_bigobject = %s",[table])
    row = cursor.fetchone()
    if row is None:
        print("Table {!s} not found".format(table))
        sys.exit(NAGIOS_WARNING)

    # Part II. check number of records in table against threshold
    cursor = bo_client.query("SELECT COUNT(*) as cnt FROM %s", [table])
    row = cursor.fetchone()
    cnt = row['cnt']

    if ( scheme == "above" and cnt > threshold ) or (scheme == "below" and cnt < threshold):
        # alert under these conditions
        print(f"[WARNING] Table {table} has {cnt} records, alert triggered since {scheme} {threshold}")
        sys.exit(NAGIOS_WARNING)

    print(f"[OK] Table {table} has {cnt} records, alert triggered if {scheme} {threshold}")
    sys.exit(NAGIOS_OK)

# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
