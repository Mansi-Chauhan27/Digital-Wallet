from celery import shared_task
from django.conf import settings
import os
import time
from apps.clients.models import RegisterUserOtp, User, Otp
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from apps.common.helper.utils import otpgen
from datetime import datetime, timedelta

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
def send_mail_task2(userid,otp,email):
    sendEmailForVerification(otp,email)
    # user = Otp(user_id=userid,otp=otp,is_used=False)
    # user.save()



# Send OTP EMAIL
def sendEmailForVerification(otp,receiver_email):
    
    # SENDER_EMAIL = settings.ADMIN_ID
    SENDER_EMAIL = str(settings.SENDER_EMAIL)
    RECEIVER_EMAIL = ['mansichauhan15@gmail.com']
    
    SUBJECT='Email Verification'

    
    if(RECEIVER_EMAIL):
        try:
            for item in RECEIVER_EMAIL :
                HTML = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8" />
                </head>
                <body>
                    Hi your otp is ,<br> <br>
                    """+str(otp)+"""
                    <br><br>
                    
                    <br>
                    <br>
                    Thank you!
                </body>
                </html>
                """
            
                message1 = Mail(from_email=SENDER_EMAIL,to_emails=str(item),subject=SUBJECT,html_content=HTML)
            
                sg = SendGridAPIClient(settings.SENDGRID_KEY)
                response = sg.send(message1)
            # return response
        except Exception as e:
            pass
            # data = {'error':'1'}
            # return data
