import sys
from kit import BigObject

# python3 ... MASTER_HOST MASTER_PORT MASTER_DB CLUSTER_NUM
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

def main():
    # verify input
    args = sys.argv

    if len(args) < 4:
        raise Exception('number of arguments not enough')

    host = args[1]
    port = int(args[2])
    db = args[3]
    cluster_num = int(args[4])
    
    # setup connection and query
    bo_client = BigObject.connect(host, port, db)
    cursor = bo_client.query("remote SELECT 1 as result")
    rows = cursor.fetchall()
    
    # get result from all remote host
    if len(rows) == 0:
        print("no remote cluster found")
        sys.exit(NAGIOS_WARNING)
        
    # verify query result with desired value
    qr_cluster_num = sum([ item['result'] for item in rows ])
    if qr_cluster_num != cluster_num:
        print("{!s} cluster found".format(qr_cluster_num))
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
    
