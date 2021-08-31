import sys
from kit import BigObject

# python3 ... HOST PORT
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

def main():
    # verify input
    args = sys.argv

    if len(args) < 3:
        raise Exception('number of arguments not enough')

    host = args[1]
    port = int(args[2])
    db = args[3]
    
    # setup connection
    bo_client = BigObject.connect(host, port, db)
    result = bo_client.query("SELECT 1 as result")
    
    # get result and verify
    row = result.fetchone()
    if row.get('result',0) != 1:
        print('SELECT 1 error')
        sys.exit(NAGIOS_WARNING)
    
    print('OK')
    sys.exit(NAGIOS_OK)
    
# : def main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
    
