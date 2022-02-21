import sys
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
    startline = "====== stats below ======"
    host_name = args[1]
    host_address = args[2]
    alert_at = float(args[3])
    remote_cmd = f"echo '{startline}' && ps -eo pid,cmd,%mem,%cpu --sort=-%mem | head -10 && free -m "

    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)

    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh connection error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)

    try:
        start =msg_stack.index(startline)
        line  = msg_stack[-3]
        [_, total, used, free, _, _, _] = line.split()
        total = float(total)
        used = float(used)
    except Exception as e:
        print("remote command response malformat {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)

    used_r = int(100*used/total)
    print( "total: {!s}MB, used: {!s}MB({!s}%), alert if >={!s}%".format( total, used, used_r, alert_at ) )
    for line in msg_stack[start:-4]:
        print(line)
    if used_r >= alert_at:
        sys.exit(NAGIOS_WARNING)

    sys.exit(NAGIOS_OK)
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
