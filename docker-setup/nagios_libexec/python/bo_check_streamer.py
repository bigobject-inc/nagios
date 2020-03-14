import sys
from kit import BigObject

# python3 ... HOST PORT DB TABLE EXPIRE_MIN
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

def main():
    # message stack
    msg_stack = []
    
    # verify input
    args = sys.argv

    if len(args) < 6:
        raise Exception('number of arguments not enough')

    host = args[1]
    port = int(args[2])
    db = args[3]
    table = args[4]
    expire_minute = int(args[5])
    
    # setup connection
    bo_client = BigObject.connect(host, port, db)
    
    # Part I. check existence on table
    cursor = bo_client.query("SELECT COUNT(*) as result from (show tables) where Tables_in_bigobject = %s",[table])
    row = cursor.fetchone()
    msg_stack += check_table(row, table)
    
    # Part II. check row_expire time and total
    cursor = bo_client.query("SELECT timestamp as `ts_row`, utc_timestamp() as `ts_now` , total FROM %s last 1", [table])
    row = cursor.fetchone()
    msg_stack += check_row(row, expire_minute)
    
    if len(msg_stack) >0 :
        print(msg_stack)
        sys.exit(NAGIOS_WARNING)
    
    print("OK")
    sys.exit(NAGIOS_OK)
    
# : def main

def check_table(row, table):
    """ check table existence """
    errors = []
    if row is None:
        # table not found
        errors.append("table not found: {!s}".format(table))
    elif row['result'] is not 1:
        errors.append("table: {!s} found, but count not 1".format(table))
        
    return errors
# :def check_table
    
def check_row(row, expire_minute):
    errors = []
    if row is None:
        # row not found
        errors.append("last row not queried")
        return errors
    
    # check timestamp of last row
    time_diff = row['ts_now'] - row['ts_row']
    diff_seconds = time_diff.total_seconds()
    threshold_seconds = 60*expire_minute
    if diff_seconds >= threshold_seconds:
        errors.append("timestamp expired {!s} seconds (threshold {!s})".format(diff_seconds, threshold_seconds))
        
    # check total
    total = row['total']
    if not (total > 0):
        errors.append("total error: {!s} found".format(total))
    
    return errors
# :def check_row

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("exception caught as follows:{!s}".format(e))
        sys.exit(NAGIOS_UNKNOWN)
    
