from django.http import HttpResponse
from django.views.generic import View
import os

from apps.clients.serializers import UserSerialzer
from apps.clients.models import User
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.devices.models import Device
from apps.devices.serializers import DeviceSerialzer
import json
 
#importing get_template from loader
from django.template.loader import get_template
 
#import render_to_pdf from util.py 
from apps.common.helper.utils import render_to_pdf 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
import email
import email.mime.application
from celery import shared_task
from celery import group
# from celery.task.sets import TaskSet, subtask
# from tasks import add

@shared_task
def userReport():    
    #getting the users
    u = User.objects.filter(is_active=True,is_customer=True,is_verified=True)
    serializer = UserSerialzer(u, many=True)
    user_list = json.loads(json.dumps(serializer.data))
    
    for item in user_list:
        for card in item['cards_detail']:
            print(card['id'])
            transaction_history = getTransactionHistory(card['id'])
            print(transaction_history['data'])
            group(generateReportAndSendMail.s('mansi9@yopmail.com',settings.SENDER_EMAIL,settings.SENDER_PASS,item['email'],transaction_history['data'],str(card['card_number'])[-4:]))()
            # generateReportAndSendMail.delay('1234','mansi9@yopmail.com',settings.SENDER_EMAIL,settings.SENDER_PASS,item['email'],transaction_history['data'],str(card['card_number'])[-4:])
            # pass
    
        

@shared_task
def generateReportAndSendMail(receiver_email,sender_email,sender_pass,useremail,transaction_history,card):
    try:
        filename_pdf = useremail+'.pdf'
        res = render_to_pdf('transaction.html',filename_pdf,{'data':useremail,'transaction':transaction_history})
        if(res):
            template = get_template('intro.html')
            context = {'card': str(card),'useremail':useremail}
            content = template.render(context)
            mail_content = content

            #The mail addresses and password
            # print(2/0)
            sender_address = sender_email
            sender_password = sender_pass
            receiver_address = receiver_email

            #Setup the MIME
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'Transaction Details.'   #The subject line

            #The body and the attachments for the mail
            message.attach(MIMEText(mail_content, 'text/html'))

            # Adding Pdf file attachment
            filename='pdf/'+filename_pdf
            fo=open(filename,'rb')
            attach = email.mime.application.MIMEApplication(fo.read(),_subtype="pdf")
            fo.close()
            attach.add_header('Content-Disposition','attachment',filename='transaction.pdf')
            message.attach(attach)

            #Create SMTP session for sending the mail
            session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
            session.starttls() #enable security
            session.login(sender_address, sender_password) #login with mail_id and password
            text = message.as_string()
            session.sendmail(sender_address, receiver_address, text)
            session.quit()

            if os.path.exists(str(filename)):
                os.remove(str(filename))
    except Exception as exc:
        # retry after 1 minute
        print(exec)
        raise generateReportAndSendMail.retry(exc=exc, countdown=60)            

@shared_task
def add(otp,receiver_email,sender_email,sender_pass,useremail,transaction_history,card):
    print('heyyy',otp,receiver_email,sender_email,sender_pass,useremail,transaction_history,card)


def getTransactionHistory(card_id):
    transaction = Transaction()
    device = Device()
    user = User()
    result={}
    card_id=card_id
    # print(transaction.get_last_month_transactions(card_id))
    transaction_query = transaction.get_last_month_transactions(card_id)
    print(transaction_query)
    transaction_serializer = TransactionSerializer(transaction_query,many=True)
    transaction_queryset = json.loads(json.dumps(transaction_serializer.data))
    device_query = device.get_all_devices()
    device_serializer = DeviceSerialzer(device_query,many=True)
    device_queryset = json.loads(json.dumps(device_serializer.data))

    data=[]
    if transaction_queryset:
        for tr in transaction_queryset:
            to = None
            fr = None
            status=None
            y=[x for x in device_queryset if x['card'] == tr['to_card_detail']['id']]
            if(y):
                to = y[0]['name']
            else:
                # pass
                to = user.get_user_email_by_id(tr['to_card_detail']['user'])
            f=[x for x in device_queryset if x['card'] == tr['from_card_detail']['id']]
            if(f):
                fr = f[0]['name']
            else:
                # pass
                fr = user.get_user_email_by_id(tr['from_card_detail']['user'])
            status = 'Credit' if(tr['to_card_detail']['id']==card_id) else 'Debit'
            source = to if(status=='Debit') else fr
            data.append({'id':tr['id'],'amount':tr['amount'],'debit_from':fr,'credit_to':to, 'to_card_id':tr['to_card_detail']['card_number'],'from_card_id':tr['from_card_detail']['card_number'],'status':status,'source':source,'created_at':tr['created_at']})
        result['data'] =data
        result['msg']='Success'
        return result
    else:
        result['data'] = {}
        return result
