import json

from braces.views import GroupRequiredMixin
from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND,
                                   HTTP_405_METHOD_NOT_ALLOWED)
from rest_framework.views import APIView

from apps.clients.models import User
from apps.devices.models import Device, DeviceAPIKey
from apps.devices.permissions import HasDeviceAPIKey
from apps.devices.serializers import DeviceSerialzer

from .models import (Card, CardDetails, GiftCard, Transaction,
                     TransactionDetails)
from .serializers import (CardDetailsSerialzer, CardSerializer,
                          TransactionDetailsSerialzer,
                          TransactionSerializer)
from apps.clients.serializers import UserSerialzer

'''
    To Get Customer Cards balance and history of all the transactions made
'''
class GetBalance(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    
    @transaction.atomic
    def post(self,request):
        result={}
        action=request.data['data']['action']
        import logging
        logger = logging.getLogger(__name__)
        logger.info('HEYYYYYYYYYYYY')
        logging.warning(request.user,request.user.groups.filter(name='customer').exists())
        # to Get BAlance or To Get History of all transactions made
        if(action=='get_balance'):
            userid=request.user.id
            queryset = Card.get_users_cards(self,userid)
            serializer = CardSerializer(queryset, many=True)
            result['data'] = serializer.data
            return Response({'data':result,'u':request.user.groups.filter(name='customer').exists()},status=HTTP_200_OK)
        else:
            data=request.data['data']
            card_id=data['card_id']
            transaction_query = Transaction.get_transactions(self,card_id)
            transaction_serializer = TransactionSerializer(transaction_query,many=True)
            transaction_queryset = json.loads(json.dumps(transaction_serializer.data))
            device_query = Device.get_all_devices(self)
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
                        to = User.get_user_email_by_id(self,tr['to_card_detail']['user'])
                    f=[x for x in device_queryset if x['card'] == tr['from_card_detail']['id']]
                    if(f):
                        fr = f[0]['name']
                    else:
                        # pass
                        fr = User.get_user_email_by_id(self,tr['from_card_detail']['user'])
                    status = 'Credit' if(tr['to_card_detail']['id']==card_id) else 'Debit'
                    source = to if(status=='Debit') else fr
                    data.append({'id':tr['id'],'amount':tr['amount'],'debit_from':fr,'credit_to':to, 'to_card_id':tr['to_card_detail']['card_number'],'from_card_id':tr['from_card_detail']['card_number'],'status':status,'source':source,'created_at':tr['created_at']})
                result['data'] =data
                result['msg']='Success'
                return Response({'data':result,'u':request.user.groups.filter(name='customer').exists()},status=HTTP_200_OK)
            else:
                return Response({},status=HTTP_404_NOT_FOUND)
        

'''
    To Transfer Money From one Card to another
'''
class TransferMoney(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    group_required = ["customer","admin","owner"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # to transfer money 
    @transaction.atomic
    def post(self,request):
        result={}
        data=request.data['data']
        action = data['action']
        verified = False
        # To check whether user is verified to make transactions
        if(action=="from_customer"):
            if(request.user.is_verified==True):
                verified = True
        elif(action=="from_device"):
            device_api_key  = DeviceAPIKey.get_device_apikey(self,data['device_id'])
            if(device_api_key):
                verified = True
        if verified:
            from_card_id = data['from_card_id']
            to_card_id = data['to_card_id']
            amount_to_be_transferred = int(data['amount_to_be_transferred'])
            from_card_id_data = Card.get_card_by_id(self,from_card_id)
            from_card_id_serializer = CardSerializer(from_card_id_data, many=False)
            balance=from_card_id_serializer.data['balance']
            to_card_id_data = Card.get_card_by_id(self,to_card_id)
            to_card_id_serializer = CardSerializer(to_card_id_data, many=False)
            to_card_id_balance=to_card_id_serializer.data['balance']
            if(int(balance)>=int(amount_to_be_transferred)):
                balance -= amount_to_be_transferred
                result['msg'] = 'Success'

                transaction_data  = {
                                'amount':amount_to_be_transferred,
                                'from_card': from_card_id,
                                'to_card':to_card_id,
                                'user': request.user.id,
                                }
                transaction_serializer = TransactionSerializer(data = transaction_data)
                transaction_serializer.is_valid()
                if transaction_serializer.is_valid(raise_exception=True):
                    transaction_serializer.save()
                    # from_card_data = Card.get_card_by_id(self,from_card_id)
                    from_card_serializer = CardSerializer(from_card_id_data, data={'balance': balance}, partial=True)
                    
                    # to_card_data = Card.get_card_by_id(self,to_card_id)
                    to_card_serializer = CardSerializer(to_card_id_data, data={'balance': to_card_id_balance+amount_to_be_transferred}, partial=True)
                    if from_card_serializer.is_valid() and to_card_serializer.is_valid():
                        from_card_serializer.save()
                        to_card_serializer.save()
                        return Response({'data':result},status=HTTP_200_OK)
                    else:
                        return Response({},HTTP_400_BAD_REQUEST)
                    
                else:
                    return Response({},HTTP_400_BAD_REQUEST)


            else:
                result['msg'] = 'Insufficient Balance'

                return Response({'data':result},status=HTTP_200_OK)
        
        else:
            return Response({'msg':'Not Verified To MAke Transactions'},status=HTTP_405_METHOD_NOT_ALLOWED)

'''
    To get Cards with respect to User/Other users Cards/ Other users Cards Includinf all devices Cards
'''
class GetCards(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    group_required = ["customer","admin","owner"]
    raise_exception = True
    redirect_unauthenticated_users = False

    
    @transaction.atomic 
    def post(self,request):
        result={}
        data=request.data['data']
        user_id=request.user.id
        action = data['action']
        
        # to get cards for logged in user
        if action == "get_users_cards":
            result={}
            queryset = Card.get_users_cards(self,user_id)
            serializer = CardSerializer(queryset, many=True)
            result['data'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

        # to get cards of particular user
        elif action == "get_users_cards_by_id":
            result={}
            user_id = data['userid']
            queryset = Card.get_users_cards(self,user_id)
            serializer = CardSerializer(queryset, many=True)
            result['data'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

        # to get cards of other users/devices(other than loggen in user)
        if action == "get_other_users_cards":
            result={}
            devices_queryset  =  Device.get_devices(self)
            # To get all Other users card
            queryset = Card.get_other_users_cards(self,user_id)
            serializer = CardSerializer(queryset, many=True)
            result['devices'] = devices_queryset
            result['customers'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

        # to get cards of only users and not devices for refund transaction
        if action == "get_users_cards_for_refund":
            result={}
            devices_queryset  =  Device.get_all_devices(self)
            device_serializer = DeviceSerialzer(devices_queryset,many=True)
            device_data = json.loads(json.dumps(device_serializer.data))
            device_card_list = [x['card'] for x in device_data]
            # To get all Other users card
            queryset = Card.get_users_cards_for_refund(self,device_card_list)
            serializer = CardSerializer(queryset, many=True)
            result['devices'] = device_serializer.data
            result['customers'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)


########################################################################################################


# to make transacion via devices using key (TODO), I dont hink it is required now or maybe in future integrations

class Transaction1(APIView):
    permission_classes = (HasDeviceAPIKey)

   
    def get(self,request):
        # print('dwef')
        # print(request.user)
        result={}

        queryset = TransactionDetails.objects.all()
        # print(queryset,'uhiuhiu')
        serializer = TransactionDetailsSerialzer(queryset, many=True)
        # print(serializer.data)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)





    def post(self,request):
        result={}
        data=request.data['data']
        queryset = CardDetails.objects.get(user_id=data['user_id'])
        serializer = CardDetailsSerialzer(queryset, many=False)
        # card = CardDetails.objects.filter(user_id=data['user_id']).values('id')
        card_id = serializer.data['id']
        tr = CardDetails.objects.filter(user_id=data['user_id']).all().values()
        # tr = TransactionDetails.objects.all().order_by('-updated_at').values().first()
        balance=serializer.data['balance']
        if card_id:
            # balance = tr['balance']
            if balance>=data['debit_amount']:
                balance +=data['credit_amount']
                balance -=data['debit_amount']
            else:
                result['msg'] = 'NOt Enough Balance'

        else:
            result['msg'] = 'Card Does Not Exists'

        transaction_data  = {'balance':balance,
                            'credit_amount':data['credit_amount'],
                            'debit_amount': data['debit_amount'],
                            'is_topup':data['is_topup'],
                            'card': [card_id]
                            }




        transaction_serializer = TransactionDetailsSerialzer(data = transaction_data)
        try:
            if transaction_serializer.is_valid(raise_exception=True):
                trans = transaction_serializer.save()
                result['data':trans]
                CardDetails.objects.filter(id=card_id).update(balance=balance)
            
        except Exception as e:
            pass
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)

##################################

from django.http import HttpResponse
from django.views.generic import View
 
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
 
 
#Creating our view, it is a class based view
class GeneratePdf(View):
    def get(self, request, *args, **kwargs):    
        #getting the users
        u = User.objects.filter(is_active=True,is_customer=True,is_verified=True)
        serializer = UserSerialzer(u, many=True)
        user_list = json.loads(json.dumps(serializer.data))
        print(json.loads(json.dumps(serializer.data)))

        #getting the template
        # res = render_to_pdf('transaction.html','test.pdf',{'data':'mansi','keywords':[{'id':1},{'id':2}]})
        # print(res)
        # if(res):
        for item in user_list:
            generateReportAndSendMail('1234','mansi9@yopmail.com',settings.SENDER_EMAIL,settings.SENDER_PASS,item['email'])
         #rendering the template
        return HttpResponse('done')
 

def generateReportAndSendMail(otp,receiver_email,sender_email,sender_pass,useremail):
    filename_pdf = 'transaction.pdf'
    res = render_to_pdf('transaction.html',filename_pdf,{'data':useremail,'keywords':[{'id':1},{'id':2}]})
    print(res)
    if(res):
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
        # Adding Pdf file attachment
        filename='pdf/'+filename_pdf
        fo=open(filename,'rb')
        attach = email.mime.application.MIMEApplication(fo.read(),_subtype="ppt")
        fo.close()
        attach.add_header('Content-Disposition','attachment',filename=filename)

        message.attach(attach)
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
            