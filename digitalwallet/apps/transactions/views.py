import json

from braces.views import GroupRequiredMixin
from django.db import transaction
from django.utils.decorators import method_decorator
# from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from rest_framework.views import APIView

from apps.clients.decorators import group_required
from apps.clients.models import User
from apps.common.helper.utils import cardgen
from apps.devices.models import Device
from apps.devices.permissions import HasDeviceAPIKey
from apps.devices.serializers import DeviceSerialzer

from .models import (Card, CardDetails, GiftCard, Transaction,
                     TransactionDetails)
from .serializers import (CardDetailsSerialzer, CardSerializer,
                          GiftCardSerializer, TransactionDetailsSerialzer,
                          TransactionSerializer)


# to get balnace and history of a user (S Done)
class GetBalance(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # to Get BAlance
    @transaction.atomic
    def post(self,request):
        result={}
        action=request.data['data']['action']
        try:
            if(action=='get_balance'):
                userid=request.user.id
                queryset = Card.get_users_cards(self,userid)
                serializer = CardSerializer(queryset, many=True)
                result['data'] = serializer.data
                result['msg']='Success'
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
                    data.append({'id':tr['id'],'amount':tr['amount'],'debit_from':fr,'credit_to':to, 'to_card_id':tr['to_card_detail']['card_number'],'from_card_id':tr['from_card_detail']['card_number'],'status':status,'source':source})
                result['data'] =data
                result['msg']='Success'

            
        except Exception as e:
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)


# to transfer money  (S Done)
class TransferMoney(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # to transfer money 
    @transaction.atomic
    def post(self,request):
        result={}
        data=request.data['data']
        action = "to_customer"
        if action == "to_customer":
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
                print(transaction_data)
                transaction_serializer = TransactionSerializer(data = transaction_data)
                transaction_serializer.is_valid()
                print(transaction_serializer.errors)
                print('transaction_serializer.is_valid',transaction_serializer.is_valid())
                if transaction_serializer.is_valid(raise_exception=True):
                    transaction_serializer.save()
                    # from_card_data = Card.get_card_by_id(self,from_card_id)
                    from_card_serializer = CardSerializer(from_card_id_data, data={'balance': balance}, partial=True)
                    
                    # to_card_data = Card.get_card_by_id(self,to_card_id)
                    to_card_serializer = CardSerializer(to_card_id_data, data={'balance': to_card_id_balance+amount_to_be_transferred}, partial=True)
                    print(from_card_serializer.is_valid(),to_card_serializer.is_valid())
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
        
# to get cards (S Done)
class GetCards(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    group_required = ["customer","admin"]
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

        if action == "get_other_users_cards":
            result={}
            devices_queryset  =  Device.get_devices(self)
            # To get all Other users card
            queryset = Card.get_other_users_cards(self,user_id)
            serializer = CardSerializer(queryset, many=True)
            result['devices'] = devices_queryset
            result['customers'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)


########################################################################################################

# to generate card Number
class GenerateCardNumber(APIView):
    permission_classes = (IsAuthenticated,)

    @method_decorator(group_required('admin'))
    @transaction.atomic
    def post(self,request):
        result={}
        card_no = cardgen()
        while  CardDetails.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        data = request.data['data']
        if card_no:
            u = User.objects.get(id=data['id'])
            card = CardDetails(user=u,card_number=card_no)
            card.save()
            result['msg'] = "Card Save Successfully"
        else:
            result['msg'] = "Error Generating Card"

        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)



# to get and add giftcards (According To Old Schema)

class GiftCardTransaction(APIView):
    permission_classes = (IsAuthenticated,)

    # to Retrieve Gift Cards
    def get(self,request):
        result={}
        queryset = GiftCard.objects.all()
        serializer = GiftCardSerializer(queryset, many=True)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)


    # to Add Gift Card
    def post(self,request):
        result={}
        # data will contain giftcard
        # data=request.data['data']
        data={'gift_card_no':'GET60','gift_card_amount':60}
        giftcard_data  = {'gift_card_no':data['gift_card_no'],
                            'amount':data['gift_card_amount'],
                            'is_active': True,   
                            }

        giftcard_serializer = GiftCardSerializer(data = giftcard_data)
        try:
            if giftcard_serializer.is_valid(raise_exception=True):
                trans = giftcard_serializer.save()
                # result['data']=trans
                result['msg']='Success'
            
        except Exception as e:
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)


# to topup money into users card (According To Old Schema)
    
class GiftCardTopup(APIView):
    permission_classes = (IsAuthenticated,)

    # to top up 
    def post(self,request):
        result={}
        # data will contain giftcard
        data=request.data['data']
        queryset = CardDetails.objects.get(user_id=data['user_id'])
        serializer = CardDetailsSerialzer(queryset, many=False)
        # card = CardDetails.objects.filter(user_id=data['user_id']).values('id')
        card_id = serializer.data['id']
        balance=serializer.data['balance']
        if card_id:
            # balance = tr['balance']
            # if balance>=data['debit_amount']:
            #     balance +=data['credit_amount']
            balance += data['credit_amount']
            # else:
            result['msg'] = 'Success'

        else:
            result['msg'] = 'Card Does Not Exists'

        gift_card_id =  data['gift_card_id'] if data['gift_card_id'] else None
        transaction_data  = {'balance':balance,
                            'credit_amount':data['credit_amount'],
                            'debit_amount': data['debit_amount'],
                            'is_topup':data['is_topup'],
                            'card': [card_id],
                            'gift_card': gift_card_id        
                            }

        transaction_serializer = TransactionDetailsSerialzer(data = transaction_data)
        try:
            if transaction_serializer.is_valid(raise_exception=True):
                trans = transaction_serializer.save()
                # result['data':trans]
                CardDetails.objects.filter(id=card_id).update(balance=balance)
                result['msg']='Success'
            
        except Exception as e:
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)
    



# to make transacion via devices using key (TODO)

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

