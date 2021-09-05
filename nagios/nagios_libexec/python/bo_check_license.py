import sys
import click
from datetime import datetime as DateTime
from datetime import timezone as TimeZone
from kit import BigObject
from kit import Fernet

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

@click.command(help='check BO license time')
@click.argument('host')
@click.argument('port')
@click.argument('db')
@click.argument('expire_days', type=int)
@click.option('--user', default='root')
@click.option('--password', default='')
def main(host, port, db, expire_days, user, password):
    """ Verify BO license via sql connection query """
    # decipher password
    if len(password) != 0:
        fernet = Fernet.getOptEnv()
        password = fernet.decrypt(password)

    # setup connection
    bo_client = BigObject.connect(host, port, db, user, password)
    cursor = bo_client.query("select value from (show config) where variables_in_config = 'license'")

    # get result and verify
    row = cursor.fetchone()
    if row is None:
        print('query error: no result found')
        sys.exit(NAGIOS_WARNING)

    message = row['value'].split('/')
    expire_dt = DateTime.strptime(message[0], '%Y-%m-%d').replace(tzinfo=TimeZone.utc)
    now_dt = DateTime.now(tz=TimeZone.utc)

    time_diff = expire_dt - now_dt
    if time_diff.total_seconds() <= 0:
        # expired in negative time_diff
        print("license expired already")
        sys.exit(NAGIOS_WARNING)

    if time_diff.days <= expire_days:
        # expired in assigned days
        print("license expired on {!s}".format(expire_dt.strftime("%Y-%m-%d")))
        sys.exit(NAGIOS_WARNING)

    print("[OK]license expired on {!s}".format(expire_dt.strftime("%Y-%m-%d")))
    sys.exit(NAGIOS_OK)

# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
