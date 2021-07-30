import html
import os
import time
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from apps.clients.models import Otp, RegisterUserOtp, User
from apps.common.helper.utils import otpgen
from django.template.loader import get_template





@shared_task
def send_mail_task2(userid,otp,email,sender_email,sender_pass):
    # sendEmailForVerification(otp,email,sender_email,sendgrid_key)
    sendEmailForVerificationUsingGmail(otp,email,sender_email,sender_pass)




'''
    Send OTP EMAIL

'''
def sendEmailForVerification(otp,receiver_email,sender_email,sendgrid_key):
    
    # SENDER_EMAIL = settings.ADMIN_ID
    SENDER_EMAIL = str(sender_email)
    RECEIVER_EMAIL = ['mansichauhan15@gmail.com']
    
    SUBJECT='Email Verification'

    
    if(RECEIVER_EMAIL):
        for item in RECEIVER_EMAIL :
            template = get_template('t.html')
            context = {'otp': str(otp)}
            content = template.render(context)
            print(content)
            print('####'+sender_email, sendgrid_key)
            message1 = Mail(from_email=SENDER_EMAIL,to_emails=str(item),subject=SUBJECT,html_content=content)
            print('ssdss',message1)
            sg = SendGridAPIClient(sendgrid_key)
            res = sg.send(message1)
            print(res.status_code, res.body, res.headers)
            

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendEmailForVerificationUsingGmail(otp,receiver_email,sender_email,sender_pass):
    template = get_template('t.html')
    context = {'otp': str(otp)}
    content = template.render(context)
    mail_content = content
    print(receiver_email,sender_email,sender_pass)
    #The mail addresses and password
    sender_address = sender_email
    sender_password = sender_pass
    receiver_address = receiver_email
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_password) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
        

@shared_task
def send_mail_task(userid):
    time.sleep(15)
    otp=otpgen()
    u = User.objects.get(id=userid)
    sendEmailForVerification(otp,u.email)
    if RegisterUserOtp.objects.filter(user=u):
        RegisterUserOtp.objects.filter(user=u).update(otp=otp,expiry=datetime.now()+timedelta(hours=2))
    else:
        user = RegisterUserOtp(user=u,otp=otp,expiry=datetime.now()+timedelta(hours=2))
        user.save()


@shared_task
def add():
    print('helloo')