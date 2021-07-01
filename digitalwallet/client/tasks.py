from celery import shared_task
from django.conf import settings
import os
import time
from client.models import RegisterUserOtp, User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from common.helper.utils import otpgen

@shared_task
def send_mail_task(userid):
    print("*****"*10)
    print("QUEUE Started")
    print("Time sleep started")
    time.sleep(15)
    print("Time sleep Ended")
    print("QUEUE Ended")
    otp=otpgen()
    u = User.objects.get(id=userid)
    sendEmailForVerification(otp,u.email)
    if RegisterUserOtp.objects.filter(user=u):
        RegisterUserOtp.objects.filter(user=u).update(otp=otp)
    else:
        user = RegisterUserOtp(user=u,otp=otp)
        user.save()




# import random as r
# # function for otp generation
# def otpgen():
#     otp=""
#     for i in range(4):
#         otp+=str(r.randint(1,9))
#     print ("Your One Time Password is ")
#     print (otp)
#     return otp

def sendEmailForVerification(otp,receiver_email):
    
    # SENDER_EMAIL = settings.ADMIN_ID
    SENDER_EMAIL = 'mfsi.mansic@gmail.com'
    print('SENDER_EMAIL',SENDER_EMAIL)
    RECEIVER_EMAIL = ['mansichauhan15@gmail.com']
    
    SUBJECT='Email Verification'

    
    if(RECEIVER_EMAIL):
        try:
            for item in RECEIVER_EMAIL :
                print(item)
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
                print(response.status_code)
                print(response.body)
                print(response.headers)
            # return response
        except Exception as e:
            print(e)
            # data = {'error':'1'}
            # return data
