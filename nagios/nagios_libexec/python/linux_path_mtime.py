import sys
import time, re
from kit import RemoteCmd

# python3 ... HOST_NAME HOST_ADDRESS PATH ALERT_AT
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
    file_path = args[3]
    alert_at = float(args[4])
    remote_cmd = "date -r {!s} +%s ".format(file_path)
    
    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)
    
    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh connection error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    
    # fetch file modified timestamp
    file_mts  = msg_stack[-2]    
    if re.match('^(\d+)$', file_mts) is None:
        raise Exception('timestamp detection error: {!s}'.format(msg_stack)) 
        sys.exit(NAGIOS_WARNING)
    
    # compute diff
    now_ts  = time.time()
    file_mts = int(file_mts)
    diff_sec = now_ts - file_mts
    diff_min = int( diff_sec / 60 )
    print("{!s} modified {!s} minutes ago, alert if modified within {!s} minutes".format(
        file_path,
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
    
