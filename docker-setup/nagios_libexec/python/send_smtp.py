from kit import Env
import sys
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# python send_smtp.py mail_to subject
SENDER = Env.get('SENDER_EMAIL')
SENDERNAME = Env.get('SENDER_NAME')

SMTP_HOST = Env.get('SMTP_HOST')
SMTP_PORT = Env.get('SMTP_PORT')
SMTP_USER=Env.get('SMTP_USER')
SMTP_PSWD=Env.get('SMTP_PSWD')

def main(argv):
    # setup input
    mail_to = argv[1]
    subject = argv[2]
    content = sys.stdin.read()
    
    # message header
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = mail_to

    # message body
    msg.attach(MIMEText(content, 'plain'))

    # Try to send the message.
    try:  
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
    except Exception as e:
        # Display an error message if something goes wrong.
        raise Exception("Error: ", e)

    try:
        # stmplib docs recommend calling ehlo() before & after starttls()
        server.starttls()
        server.ehlo()
    except:
        # some SMTP ignore TLS
        pass

    try:
        server.login(SMTP_USER, SMTP_PSWD)
    except:
        # some SMTP ignore login
        pass


    try:
        server.sendmail(SENDER, mail_to, msg.as_string())
        server.close()
    except Exception as e:
        # Display an error message if something goes wrong.
        raise Exception("Error: ", e)
    else:
        print ("Email sent!")
    
# :def main

if __name__ == "__main__":
    main( sys.argv )
