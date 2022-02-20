import sys
from datetime import datetime as DateTime
from kit import RemoteCmd

# python3 ... HOST_NAME HOST_ADDRESS ALERT_AT
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3


def main():
    # verify input
    args = sys.argv

    if len(args) < 4:
        raise Exception('number of arguments not enough')

    # setup parameter
    host_name = args[1]
    host_address = args[2]
    alert_at = int(args[3])
    remote_cmd = "chage -li \$(whoami) | grep 'Password expires' && date '+%Y-%m-%d'"

    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)

    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh connection error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)

    # parse final desired information
    line = msg_stack[-3]
    date_expire = line.split(":")[-1].strip()

    line = msg_stack[-2]
    date_now = line.strip()

    # health check based on result
    if date_expire == "never":
        # in case of never expire
        print("password has no expiration date")
        sys.exit(NAGIOS_OK)

    dt_now = DateTime.strptime(date_now, "%Y-%m-%d")
    dt_exp = DateTime.strptime(date_expire, "%Y-%m-%d")

    time_diff = dt_exp - dt_now
    if time_diff.total_seconds() <= 0:
        # expired in negative time_diff
        print("password change time expired already")
        sys.exit(NAGIOS_WARNING)

    if time_diff.days <= alert_at:
        # expired in assigned days
        print("password expired on {!s}".format(dt_exp.strftime("%Y-%m-%d")))
        sys.exit(NAGIOS_WARNING)

    print("[OK] password expired on {!s}, alert at {!s} days prior".format(dt_exp.strftime("%Y-%m-%d"), alert_at))
    sys.exit(NAGIOS_OK)
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
