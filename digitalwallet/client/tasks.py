from celery import shared_task
from django.conf import settings
import os
import time
from client.models import RegisterUser, User

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
    user = RegisterUser(user=u,otp=otp)
    user.save()




import random as r
# function for otp generation
def otpgen():
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    print ("Your One Time Password is ")
    print (otp)
    return otp
    
