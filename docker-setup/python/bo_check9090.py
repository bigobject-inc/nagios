import sys, json
import urllib.request

# python3 ... HOST PORT
NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

def main():
    # verify input
    args = sys.argv

    if len(args) < 2:
        raise Exception('number of arguments not enough')

    host = args[1]
    port = int(args[2])
    
    # setup request
    request = urllib.request.Request(
        "http://{!s}:{!s}/api".format(host,port),
        method='POST'
    )
    data = {
        'stmt': "SELECT 1 as result"
    }
    
    # send request
    try:
        res = urllib.request.urlopen(request, json.dumps(data).encode('utf-8'))
    except Exception as e:
        print("error when call API {!s}".format(e))
        sys.exit(NAGIOS_WARNING)
    
    # receive response from API
    res_rtn = json.loads(res.read().decode('utf-8'))
    if res_rtn['retcode'] is not 0:
        print("ret code error when calling BO 9090")
        sys.exit(NAGIOS_WARNING)
    
    # verify results
    result = res_rtn.get('results', [])
    if len(result[0]) == 0:
        print("error: no query result")
        sys.exit(NAGIOS_WARNING)
    if result[0][0] is not 1:
        print("error: query result should be 1")
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
    
