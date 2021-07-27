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
def send_mail_task2(userid,otp,email,sender_email,sendgrid_key):
    sendEmailForVerification(otp,email,sender_email,sendgrid_key)




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
            message1 = Mail(from_email=SENDER_EMAIL,to_emails=str(item),subject=SUBJECT,html_content=content)
        
            sg = SendGridAPIClient(sendgrid_key)
            res = sg.send(message1)
            


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