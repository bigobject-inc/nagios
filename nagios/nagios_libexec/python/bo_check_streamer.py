import sys
import click
from kit import BigObject
from kit import Fernet

# python3 ... HOST PORT DB TABLE EXPIRE_MIN
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

@click.command(help='check BO streamer')
@click.argument('host')
@click.argument('port')
@click.argument('db')
@click.argument('table')
@click.argument('expire_minute', type=int)
@click.option('--user', default='root')
@click.option('--password', default='')
def main(host, port, db, table, expire_minute, user, password):
    """ check bo streamer with an expiring threshold """
    # message stack
    msg_stack = []

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

    # Part II. check row_expire time and total
    cursor = bo_client.query("SELECT timestamp as `ts_row`, utc_timestamp() as `ts_now` , total FROM %s last 1", [table])
    row = cursor.fetchone()
    if row is None:
        print('no record found in table {!s}'.format(table))
        sys.exit(NAGIOS_WARNING)

    # check timestamp of last row
    time_diff = row['ts_now'] - row['ts_row']
    diff_seconds = time_diff.total_seconds()
    diff_minute = int(diff_seconds/60)
    threshold_seconds = 60*expire_minute
    if diff_seconds >= threshold_seconds:
        print("data expired by {!s} minutes (alert if >= {!s} minute)" \
            .format(diff_minute, expire_minute)
        )
        sys.exit(NAGIOS_WARNING)

    # check total
    total = row['total']
    if not (total > 0):
        print("total error: {!s} found".format(total))
        sys.exit(NAGIOS_WARNING)

    print("data expired by {!s} minutes (alert if >= {!s} minute)" \
        .format(diff_minute, expire_minute)
    )
    sys.exit(NAGIOS_OK)

# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
