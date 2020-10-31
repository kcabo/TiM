import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def send_mail_with_csv(user, csv, date_obj):
    msg = MIMEMultipart()
    msg["Subject"] = date_obj.strftime('%m.%d.time')
    msg["To"] = user.email
    msg["From"] = os.environ['SENDER_GMAIL_ACCOUNT']
    msg["Bcc"] = os.environ['KCABO_ADDRESS']
    msg.attach(MIMEText('\n\n\n'+ user.name,'plain','utf-8'))

    attachment = MIMEText(csv, 'plain', 'utf-8-sig')
    attachment.add_header('Content-Disposition', 'attachment', filename = date_obj.strftime('%Y.%m.%d.csv'))
    msg.attach(attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com') as smtp:
        smtp.login(os.environ['SENDER_GMAIL_ACCOUNT'], os.environ['GMAIL_APPLICATION_PASSWORD'])
        smtp.send_message(msg)
