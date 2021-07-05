from client.models import User
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
from .models import CardDetails, GiftCard, Task, TransactionDetails
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from common.helper.utils import cardgen
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import CardDetailsSerialzer, TransactionDetailsSerialzer, GiftCardSerializer
from devices.permissions import HasDeviceAPIKey


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



class GenerateCardNumber(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

    @method_decorator(group_required('admin'))
    def post(self,request):
        print('dwef')
        print(request.user)
        result={}
        card_no = cardgen()
        while  CardDetails.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        print('request.data',request.data)
        if card_no:
            u = User.objects.get(id=request.data['id'])
            card = CardDetails(user=u,card_number=card_no)
            card.save()
            print(card.card_number,'card_number')
            result['msg'] = "Card Save Successfully"
        else:
            result['msg'] = "Error Generating Card"

        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)




class Transaction(APIView):
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




class GiftCardTransaction(APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')

    def get(self,request):
        result={}
        queryset = GiftCard.objects.all()
        serializer = GiftCardSerializer(queryset, many=True)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)


    # to top up 
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
    