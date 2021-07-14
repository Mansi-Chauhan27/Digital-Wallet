from apps.client.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
# from django.contrib.auth.models import User
from rest_framework import generics, serializers
from .models import CardDetails, GiftCard, Task, TransactionDetails, Card, Transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from common.helper.utils import cardgen
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CardDetailsSerialzer, TransactionDetailsSerialzer, GiftCardSerializer, CardSerializer, TransactionSerializer
from apps.devices.permissions import HasDeviceAPIKey
from django.db.models import Q
from apps.devices.models import Device
from django.db import transaction


# from transaction.models import Card

# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     print('queryset',queryset)
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer

#     print(serializer_class.data)

   
# @csrf_exempt
# @api_view(["POST","GET"])
# @permission_classes((AllowAny,))
# @login_required
# # @admin_required
# # @group_required('admin')
# def generateCardNumber(request):

#     print('dwef')
#     print(request.user)
#     result={}
#     card_no = cardgen()
#     while  CardDetails.objects.filter(card_number=int(card_no)) :
#         card_no = cardgen()

#     print('request.data',request.data)
#     if card_no:
#         u = User.objects.get(id=request.data['id'])
#         card = CardDetails(user=u,card_number=card_no)
#         card.save()
#         print(card.card_number,'card_number')
#         result['msg'] = "Card Save Successfully"
#     else:
#         result['msg'] = "Error Generating Card"
#     return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
#     # return Response({'msg': 'Success'},status=HTTP_200_OK)


# to generate card Number
class GenerateCardNumber(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

    @method_decorator(group_required('admin'))
    @transaction.atomic
    def post(self,request):
        print(request.user)
        result={}
        card_no = cardgen()
        while  CardDetails.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        print('request.data',request.data)
        data = request.data['data']
        print(data)
        if card_no:
            u = User.objects.get(id=data['id'])
            card = CardDetails(user=u,card_number=card_no)
            card.save()
            print(card.card_number,'card_number')
            result['msg'] = "Card Save Successfully"
        else:
            result['msg'] = "Error Generating Card"

        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)


# to make transacion via devices using key

class Transaction1(APIView):
    permission_classes = (HasDeviceAPIKey)
    print('sdafdas')

    # serializer_class = TransactionDetailsSerialzer

    # def get(self, request, *args, **kwargs):
    #     serializer =  self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user=serializer.save()
    #     print('erfsdfsdf',user)
    #     return Response({
    #         "token":Token.objects.get(user=user).key
    #     })
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


    # def get(self,request,id):
    #     print('dwef')
    #     print(request.user)
    #     result={}
    #     queryset = TransactionDetails.objects.get(card=id)
    #     print(queryset,'uhiuhiu')
    #     serializer = TransactionDetailsSerialzer(queryset,manny=False)
    #     print(serializer.data)
    #     return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
    #     # return Response({'msg': 'Success'},status=HTTP_200_OK)



    # def post(self,request):
    #     print('dwef')
    #     print(request.user,request.user.id)
    #     result={}
    #     data=request.data['data']
    #     print(request.data,'data',data)
    #     queryset = CardDetails.objects.get(user_id=data['user_id'])
    #     print(queryset,'uhiuhiu')
    #     serializer = CardDetailsSerialzer(queryset, many=False)
    #     print(serializer.data)
    #     # card = CardDetails.objects.filter(user_id=data['user_id']).values('id')
    #     card_id = serializer.data['id']
    #     print('card',card_id)
    #     tr = CardDetails.objects.filter(user_id=data['user_id']).all().values()
    #     # tr = TransactionDetails.objects.all().order_by('-updated_at').values().first()
    #     print('fadfadfadfsad',tr)
    #     balance=serializer.data['balance']
    #     # if tr:
    #     #     balance = tr['balance']
    #     #     if balance>data['debit_amount']:
    #     #         balance = balance+data['credit_amount']
    #     #         balance = balance-data['debit_amount']
    #     #     else:
    #     #         result['msg'] = 'NOt Enough Balance'

    #     # else:
    #     #     if data['credit_amount']<data['debit_amount']:
    #     #         result['msg'] = 'Credit amount should be greater than Debit'

    #     #     else:
    #     #         balance += data['credit_amount']


    #     # print('balance',balance)
    #     # transaction_data  = {'balance':balance,
    #     #                     'credit_amount':data['credit_amount'],
    #     #                     'debit_amount': data['debit_amount'],
    #     #                     'is_topup':data['is_topup'],
    #     #                     'card': [card_id]
    #     #                     }




    #     # serializer = TransactionDetailsSerialzer(data = transaction_data)
    #     # print('serializer',serializer)
    #     # try:
    #     #     if serializer.is_valid(raise_exception=True):
    #     #         print(serializer.validated_data)
    #     #         trans = serializer.save()
    #     #         print(trans)
    #     # except Exception as e:
    #     #     print(e)
    #     return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
    #     # return Response({'msg': 'Success'},status=HTTP_200_OK)



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

        print('balance',balance)
        transaction_data  = {'balance':balance,
                            'credit_amount':data['credit_amount'],
                            'debit_amount': data['debit_amount'],
                            'is_topup':data['is_topup'],
                            'card': [card_id]
                            }




        transaction_serializer = TransactionDetailsSerialzer(data = transaction_data)
        print('serializer',transaction_serializer)
        try:
            if transaction_serializer.is_valid(raise_exception=True):
                trans = transaction_serializer.save()
                print('balance',balance)
                result['data':trans]
                CardDetails.objects.filter(id=card_id).update(balance=balance)
            
        except Exception as e:
            print(e)
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)


# to get and add giftcards

class GiftCardTransaction(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

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
        print('serializer',giftcard_serializer)
        try:
            if giftcard_serializer.is_valid(raise_exception=True):
                trans = giftcard_serializer.save()
                print('fdsfses',trans)
                # result['data']=trans
                result['msg']='Success'
            
        except Exception as e:
            print(e)
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)


# to topup money into users card
    
class GiftCardTopup(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

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

        print('balance',balance)
        gift_card_id =  data['gift_card_id'] if data['gift_card_id'] else None
        transaction_data  = {'balance':balance,
                            'credit_amount':data['credit_amount'],
                            'debit_amount': data['debit_amount'],
                            'is_topup':data['is_topup'],
                            'card': [card_id],
                            'gift_card': gift_card_id        
                            }

        transaction_serializer = TransactionDetailsSerialzer(data = transaction_data)
        print('serializer',transaction_serializer)
        try:
            if transaction_serializer.is_valid(raise_exception=True):
                trans = transaction_serializer.save()
                print('balance',balance)
                # result['data':trans]
                CardDetails.objects.filter(id=card_id).update(balance=balance)
                result['msg']='Success'
            
        except Exception as e:
            print(e)
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)
    



from braces.views import GroupRequiredMixin

# to get balnace and history of a user
class GetBalance(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')
    #required
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # to Retrieve Gift Cards
    def get(self,request):
        print(request.user,'frerere')
        result={}
        queryset = GiftCard.objects.all()
        serializer = GiftCardSerializer(queryset, many=True)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)


    # to Get BAlance
    @transaction.atomic
    def post(self,request):
        result={}
        action=request.data['data']['action']
        print(request.user,'frerere')
        try:
            if(action=='get_balance'):
                print(request.data)
                # userid=request.data['data']['user_id']
                userid=request.user.id
                # queryset = Card.objects.filter(user_id=userid)
                queryset = Card.getUsersCards(self,userid)
                serializer = CardSerializer(queryset, many=True)
                result['data'] = serializer.data
                result['msg']='Success'
            else:
                print(request.data)
                data=request.data['data']
                card_id=data['card_id']
                # card_id = 1
                # queryset = list(Card.objects.filter(id=4).values('id'))
                # card_id_list = [d['id'] for d in queryset]
                ###############
                # serializer = CardSerializer(queryset, many=True)
                # print('serializer.data[]',serializer.data)
                # for item in serializer.data:
                #     print(item)
                # print(queryset,card_id_list)
                # Q(first_name__startswith='R')|Q(last_name__startswith='D')
                # transaction_queryset = list(Transaction.objects.filter(Q(to_card = card_id)|Q(from_card = card_id)).values('id','to_card__card_number','to_card__id','to_card__user_id','from_card__id','from_card__user_id','amount','user__email','from_card__card_number').all())
                transaction_queryset = Transaction.getTransactionDetailsByCardId(self,card_id)
                # device_queryset = list(Device.objects.all().values('id','name','card__id'))
                device_queryset = Device.getAllDevices(self)
                # user_queryset = list(Device.objects.all().values('id','email','card__id'))
                # transaction_queryset = Transaction.objects.get(to_card__in=card_id_list,from_card__in=card_id_list).values('to_card__card_number','amount','created_at').device_set.all()
                # print(list(transaction_queryset),'dfsdfdsf',device_queryset)
                data=[]
                
                for tr in transaction_queryset:
                    to = None
                    fr = None
                    status=None
                    print(tr['to_card__id'])
                    y=[x for x in device_queryset if x['card__id'] == tr['to_card__id']]
                    if(y):
                        to = y[0]['name']
                    else:
                        # pass
                        # to=list(User.objects.filter(id=tr['to_card__user_id']).values('email'))[0]['email']
                        to = User.getUserEmailById(self,tr['to_card__user_id'])
                    f=[x for x in device_queryset if x['card__id'] == tr['from_card__id']]
                    if(f):
                        fr = f[0]['name']
                    else:
                        # pass
                        # fr = list(User.objects.filter(id=tr['from_card__user_id']).values('email'))[0]['email']
                        fr = User.getUserEmailById(self,tr['from_card__user_id'])
                    status = 'Credit' if(tr['to_card__id']==card_id) else 'Debit'
                    source = to if(status=='Debit') else fr
                    data.append({'id':tr['id'],'amount':tr['amount'],'debit_from':fr,'credit_to':to, 'to_card_id':tr['to_card__card_number'],'from_card_id':tr['from_card__card_number'],'status':status,'source':source})
                result['data'] =data
                result['msg']='Success'

            
        except Exception as e:
            print(e)
            result['msg']='Error'
        return Response({'data':result},status=HTTP_200_OK)


# to transfer money 
class TransferMoney(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # to transfer money 
    @transaction.atomic
    def post(self,request):
        result={}
        # data will contain giftcard
        data=request.data['data']
        print('hiuhiho',data)
        action = "to_customer"
        if action == "to_customer":
            from_card_id = data['from_card_id']
            to_card_id = data['to_card_id']
            amount_to_be_transferred = int(data['amount_to_be_transferred'])
            # from_card_id_data = Card.objects.get(id=from_card_id)
            from_card_id_data = Card.getCardById(self,from_card_id)
            from_card_id_serializer = CardSerializer(from_card_id_data, many=False)
            # card = CardDetails.objects.filter(user_id=data['user_id']).values('id')
            # card_id = serializer.data['id']
            balance=from_card_id_serializer.data['balance']
            print('balancebalance',balance,balance>amount_to_be_transferred)
            # to_card_id_data = Card.objects.get(id=to_card_id)
            to_card_id_data = Card.getCardById(self,to_card_id)
            to_card_id_serializer = CardSerializer(to_card_id_data, many=False)
            # card = CardDetails.objects.filter(user_id=data['user_id']).values('id')
            # card_id = serializer.data['id']
            to_card_id_balance=to_card_id_serializer.data['balance']
            if(int(balance)>=int(amount_to_be_transferred)):
                # balance = tr['balance']
                # if balance>=data['debit_amount']:
                #     balance +=data['credit_amount']
                balance -= amount_to_be_transferred
                # else:
                result['msg'] = 'Success'

                transaction_data  = {
                                'amount':amount_to_be_transferred,
                                'from_card': from_card_id,
                                'to_card':to_card_id,
                                'user': request.user.id,
                                }

                transaction_serializer = TransactionSerializer(data = transaction_data)
                print('serializer',transaction_serializer)
                # try:
                if transaction_serializer.is_valid(raise_exception=True):
                    trans = transaction_serializer.save()
                    print('balance',balance)
                    # result['data':trans]
                    Card.objects.filter(id=from_card_id).update(balance=balance)
                    Card.objects.filter(id=to_card_id).update(balance=to_card_id_balance+amount_to_be_transferred)
                    result['msg']='Success'
                
                # except Exception as e:
                #     print(e)
                else:
                    result['msg']='Error'


            else:
                result['msg'] = 'Insufficient Balance'

            # print('balance',balance)
            # gift_card_id =  data['gift_card_id'] if data['gift_card_id'] else None
            return Response({'data':result},status=HTTP_200_OK)
        
# to get cards
class GetCards(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    group_required = ["customer","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False

    
    @transaction.atomic 
    def post(self,request):
        result={}
        data=request.data['data']
        # userid=data['userid']
        userid=request.user.id
        action = data['action']
        if action == "get_users_cards":
            result={}
            # queryset = Card.objects.filter(user=userid)
            queryset = Card.getUsersCards(self,userid)
            serializer = CardSerializer(queryset, many=True)
            result['data'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        elif action == "get_users_cards_by_id":
            result={}
            # queryset = Card.objects.filter(user=userid)
            userid = data['userid']
            queryset = Card.getUsersCards(self,userid)
            serializer = CardSerializer(queryset, many=True)
            result['data'] = serializer.data
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

        # if action == "get_other_users_cards":
        #     result={}
        #     devices_queryset  =  list(Device.objects.filter(~Q(card=None)).values('card__id','name'))
        #     print('devices_querysetdevices_queryset',devices_queryset)
        #     card_id_list = [d['card__id']  for d in devices_queryset]
        #     print(devices_queryset,'fdf')
        #     queryset = list(Card.objects.filter(~Q(user=userid)).filter(~Q(id__in=card_id_list)).values())
        #     print('sdsfjjjjjjds',queryset)
        #     # serializer = CardSerializer(queryset, many=True)
        #     # result['data'] = serializer.data
        #     result['devices'] = devices_queryset
        #     result['customers'] = queryset
        #     return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

        if action == "get_other_users_cards":
            result={}
            # devices_queryset  =  list(Device.objects.filter(~Q(card=None),active=True).values('card__id','name','active'))
            devices_queryset  =  Device.getDevices(self)
            # print('devices_querysetdevices_queryset',devices_queryset)
            card_id_list = [d['card__id']  for d in devices_queryset]
            # print(devices_queryset,'fdf')
            # To get all users card
            # queryset = list(Card.objects.filter(~Q(user=userid)).values())
            queryset = Card.getOtherUsersCards(self,userid)
            # print(queryset)
            # serializer = CardSerializer(queryset, many=True)
            # result['data'] = serializer.data
            result['devices'] = devices_queryset
            result['customers'] = queryset
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
