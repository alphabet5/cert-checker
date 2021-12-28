import ssl
from datetime import datetime, timedelta
import re
import os
import smtplib
import schedule
import ssl
import socket
import time
import sys
from rich.traceback import install
from rich import Console
log_locals = (os.environ['LOG_LOCALS'].lower() not in ['y', 't', 'true', 'yes'])
install(show_locals=log_locals)
console = Console()


def check_email(email):
    regex = '^[a-z0-9-]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.search(regex, email):
        raise Exception('Invalid email format in ' + email)


def check_timedelta(timedelta):
    regex = '\d+(d|m|s)'
    if not re.search(regex, timedelta):
        raise Exception('Invalid time format in ' + timedelta)


def send_email(smtp, sender, receivers, message):
    try:
        smtp_obj = smtplib.SMTP(smtp)
        smtp_obj.sendmail(sender, receivers, message)
        console.print("Successfully sent email to " + str(receivers) + "at " + str(datetime.now()))
    except smtplib.SMTPException:
        console.print("Failed to send email.")
        console.print_exception()
        console.print(traceback.format_exc())


def check_cert(domain):
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=domain,
        )
        conn.connect((domain, 443))
        ssl_info = conn.getpeercert()
        expiry_date = datetime.strptime(ssl_info['notAfter'], r'%b %d %H:%M:%S %Y %Z')
        return expiry_date
    except:
        console.print_exception(show_locals=log_locals)
        raise Exception("Certificate check failed.")


def check_schedule(domains, times, smtp_info):
    for domain in domains:
        exp = check_cert(domain)
        if (exp - datetime.now()) > max(times):
            notifications_sent[domain] = []
        else:
            for timed in times:
                if timed not in notifications_sent[domain]:
                    if (exp - datetime.now()) < timed:
                        body = domain + ' certificate will expire on ' + str(exp)
                        send_email(smtp, sender, receivers, message + body)
                        notifications_sent[domain].append(timed)
                        console.print(str(datetime.now()) + ' ' + body)

if __name__ == '__main__':
    try:
        domains = os.getenv('DOMAINS').split(',')
        console.print(domains)
        smtp = os.getenv('SMTP_RELAY')
        times_str = os.getenv('NOTIFICATION_TIME').split(',')
        times = list()
        for timed in times_str:
            check_timedelta(timed)
            if 's' in timed:
                times.append(timedelta(seconds=int(timed.strip('s'))))
            elif 'd' in timed:
                times.append(timedelta(days=int(timed.strip('d'))))
            elif 'm' in timed:
                times.append(timedelta(minutes=int(timed.strip('m'))))
        receivers = list(set(os.getenv('NOTIFICATION_EMAIL').split(',')))
        for receiver in receivers:
            check_email(receiver)
        sender = os.getenv('SENDER')
        check_email(sender)
        message = "From: "+sender+"\nTo: " + ", ".join(receivers)+"\nSubject: Certificate Expiration Notice\n\n"
        smtp_info = {'smtp': smtp,
                     'sender': sender,
                     'receivers': receivers,
                     'message': message}
        notifications_sent = {domain: [] for domain in domains}
        schedule.every().second.do(check_schedule, domains, times, smtp_info)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except:
        console.print_exception(show_locals=log_locals)
        sys.exit(1)

