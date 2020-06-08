import sys
import re
from kit import RemoteCmd

# python3 ... HOST_NAME HOST_ADDRESS PROCESS ALERT_AT
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
    process = args[3]
    alert_at = int(args[4])
    remote_cmd = "ps ax".format(process)
    
    # send remote command via SSH
    res = RemoteCmd.commit(host_name, host_address, remote_cmd)
    
    # message stack
    msg_stack = res.split('\n')
    if len(msg_stack)<=2 :
        print("ssh connection error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    
    # filter process info
    process_list = [ line for line in msg_stack \
        if re.match("^\d+", line) is not None
    ]
    if len(process_list) == 0:
        print("ps ax parse error: {!s}".format(msg_stack))
        sys.exit(NAGIOS_WARNING)
    
    ps_stack = []
    for line in process_list:
        match = re.match("^(\d+)(\s+)(\S+)(\s+)(\S+)(\s+)(\S+)(\s+)(.+)", line)
        if match is None:
            print("single line of ps ax parse error: {!s}".format(msg_stack))
            sys.exit(NAGIOS_WARNING)
        
        ps = match.group(9)
        if ps.find(process)>=0:
            ps_stack.append(ps)
    # iterate over each process found in "ps ax"
    
    # print result
    print("{!s} has found {!s} results in process, alert if results found < {!s}. (process list : {!s})"\
        .format( process, len(ps_stack), alert_at, ps_stack)
    )
    if len(ps_stack) < alert_at:
        sys.exit(NAGIOS_WARNING)
    
    sys.exit(NAGIOS_OK)
    
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
    
