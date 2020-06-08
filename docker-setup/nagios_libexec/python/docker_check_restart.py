import sys
import dateutil.parser
from datetime import datetime as DateTime
from kit import RemoteCmd

# python3 ... HOST_NAME HOST_ADDRESS CONTAINER_ID ALERT_AT
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

def main():
    # verify input
    args = sys.argv

    if len(args) < 5:
        raise Exception('number of arguments not enough')

    # setup parameter
    host_name = args[1]
    host_address = args[2]
    container_id = args[3]
    alert_at = float(args[4])
    remote_cmd = "docker inspect {!s} --format '{{{{.State.FinishedAt}}}}'  && date '+%Y-%m-%dT%H:%M:%S%:z' ".format(container_id)
    
    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)
    
    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh connection error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    dt_str_finish  = msg_stack[-3]
    dt_str_now  = msg_stack[-2]
    try:
        dt_finish = dateutil.parser.isoparse(dt_str_finish)
        dt_now = dateutil.parser.isoparse(dt_str_now)
    except Exception as e:
        print("remote command response malformat {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    
    
    dt_diff = dt_now - dt_finish
    diff_sec = dt_diff.total_seconds()
    diff_min = int( diff_sec / 60 )
    print("{!s} ends at {!s} ({!s} minute ago), alert if < {!s} min".format(
        container_id,
        dt_finish.strftime('%Y-%m-%dT%H:%M:%S%Z'),
        diff_min,
        alert_at
    ) )
    if diff_min < alert_at:
        sys.exit(NAGIOS_WARNING)
    
    sys.exit(NAGIOS_OK)
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
    
