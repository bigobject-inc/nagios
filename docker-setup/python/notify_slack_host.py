import sys
import logging
import json
import os
import urllib.request

# python notify_slack_host.py "$NOTIFICATIONTYPE$" "$HOSTNAME$" "$HOSTADDRESS$" "$HOSTSTATE$" "$HOSTOUTPUT$" "$LONGDATETIME$"
SLACK_URL=os.getenv('SLACK_URL')
FOOTER_ICON="https://www.nagios.org/wp-content/uploads/2015/06/favicon.ico"

COLOR = {
    "UP": "#00CC00",
    "DOWN": "#EE0000",
    "DEFAULT": "#CCCCCC"
}

def main(argv):
    data = {
        "attachments": [
            {
                "color": COLOR.get(argv[4],COLOR['DEFAULT']), 
                "title": "Host {!s} notification".format(argv[1]),
                "text": "Host:        {!s}\nIP:             {!s}\nState:        {!s}".format(argv[2],argv[3],argv[4])
            },
            {
                "color": COLOR.get(argv[4],COLOR['DEFAULT']), 
                "title": "Additional Info :", 
                "text": "\n{!s}".format(argv[5]),
                "footer": "Nagios notification: {!s}".format(argv[6]), 
                "footer_icon": "$FOOTER_ICON"
            }
        ]
    }
    
    body_str = json.dumps(data).encode()
    request = urllib.request.Request(SLACK_URL, method='POST')
    request.add_header('Content-type','application/json; charset=utf-8')
    urllib.request.urlopen(request, body_str)
    
# :def main

if __name__ == "__main__":
    main( sys.argv )
