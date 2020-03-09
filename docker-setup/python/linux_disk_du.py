import sys
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
    path = args[3]
    alert_at = float(args[4])
    remote_cmd = "du -sm {!s}".format(path)
    
    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)
    
    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh response malformat {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    line = msg_stack[-2]
    try:
        [used_mb, path] = line.split()
        used_mb = float(used_mb)
    except Exception as e:
        print("remote command response malformat {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
        
    print( "{!s} has {!s} MB (alert at: {!s} MB)".format( path, used_mb, alert_at ) )
    if used_mb >= alert_at:
        sys.exit(NAGIOS_WARNING)
        
    sys.exit(NAGIOS_OK)
    
    
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
    
