import re
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from .serializers import OtpSerialzer, RegisterSerializer, RegisterUserOtpSerialzer, UserSerialzer
from rest_framework import generics, serializers
from .models import User, RegisterUserOtp, Otp
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from apps.transaction.models import CardDetails, Task, Card
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm
from rest_framework.permissions import IsAuthenticated
from datetime import datetime,timedelta
from django.utils import timezone
from apps.client.tasks import send_mail_task, send_mail_task2
from apps.common.helper.utils import cardgen
from django.db.models import Q
from braces.views import GroupRequiredMixin
from django.db import transaction
from apps.common.helper.utils import otpgen
from dateutil import parser

# Need to ask about group ... query to model
# USER REGISTRATION
class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    # print('queryset',queryset)
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @transaction.atomic 
    def post(self, request, *args, **kwargs):
    # try:
        serializer =  self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # print('erfsdfsdf',serializer.validated_data)
        user=serializer.save()
        
        user_type=None
        if(request.data['is_admin']=='true'):
            my_group = Group.objects.get(name='admin') 
            user_type='admin'
            my_group.user_set.add(user)
            # generateCardNumber(self,user.id,balance=10000)
        elif(request.data['is_customer']=='true'):
            my_group = Group.objects.get(name='customer') 
            user_type='customer'
            my_group.user_set.add(user)
            # generateCardNumber(self,user.id,balance=0)
        elif(request.data['is_owner']=='true'):
            my_group = Group.objects.get(name='owner') 
            user_type='owner'
            my_group.user_set.add(user)

        

        return Response({
            "token":Token.objects.get(user=user).key,'msg':'Success','is_admin':request.data['is_admin'], 'user_type':user_type
        })
    
    

@api_view(["POST","GET"])
@permission_classes((AllowAny,))
def login(request):
    # username = request.data.get("username")
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'},
                            status=HTTP_400_BAD_REQUEST)
        user = authenticate(email=email, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        user_type=None
        if(user.is_admin==False and user.is_customer==False) :
            user_type='owner'
        elif(user.is_admin==True):
            user_type='admin'
        else:
            user_type='customer'
        return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin, 'user_type':user_type },
                        status=HTTP_200_OK)
    # else:
    #     return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
    #                     status=HTTP_200_OK)


#  FOR OTP GENERATION AND VERIFICATION
class OtpView(APIView):
    permission_classes = (IsAuthenticated,)
    
    # generate (S Done) add otp?
    def get(self,request):

        user_id = request.user.id
        email_id = request.user.email
        if user_id is None:
            return Response({'error': 'Please provide otp'},
                            status=HTTP_400_BAD_REQUEST)
        
        else:
            otp=otpgen()
            send_mail_task2.delay(user_id,otp,email_id)
            return Response({'msg': 'Otp Send Successfully'},status=HTTP_201_CREATED)
    
    # verify (S Done)
    
    def post(self,request):
        otp = request.data.get("otp")
        if otp is None:
            return Response({'error': 'Please provide otp'},
                            status=HTTP_400_BAD_REQUEST)
        
        o = Otp.get_latest_otp_of_user(self,request.user.id)
        serializer = OtpSerialzer(o,many=False)
        otp_data = serializer.data
        if otp_data:
            if(otp_data['otp']==int(otp) and timezone.now()<parser.parse(otp_data['created_at'])+timedelta(hours=2)):
                user_data = User.getUserById(self,userid=request.user.id)
                user_serializer = UserSerialzer(user_data, data={'is_verified': True}, partial=True)

                otp_data = Otp.get_otp_id(int(otp))
                otp_serializer = OtpSerialzer(otp_data,data={'is_used': True}, partial=True)

                if(user_serializer.is_valid() and otp_serializer.is_valid()):
                    user_serializer.save()
                    otp_serializer.save()
                    return Response({'success': 'Verified','msg':'Success'},status=HTTP_200_OK)
                else:
                    return Response(status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid Otp','msg':'Error'},status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User Already Verified'},status=HTTP_404_NOT_FOUND)
        
        
# CUSTOMERS (S Done)
class Customers(APIView):
    permission_classes = (IsAuthenticated,)
    
    # TO GET ALL THE CUSTOMERS
    @method_decorator(group_required('admin'))
    def get(self, request, *args, **kwargs):
        u = User.get_all_customers(self)
        serializer = UserSerialzer(u, many=True)
        if serializer.data:
            return Response({'msg': 'Success','data':serializer.data},status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

    # TO MAKE CUSTOMER INACTIVE
    def put(self, request, format=None):
        result={}
        user_data = User.getUserById(self,userid=request.data['data']['id'])
        serializer = UserSerialzer(user_data, data={'is_active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 


# OWNERS (S Done)
class Owners(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = "admin"
    raise_exception = True
    redirect_unauthenticated_users = False

    # TO GET ALL THE RETAILERS
    def get(self, request, *args, **kwargs):
        u = User.get_all_retailers(self)
        serializer = UserSerialzer(u, many=True)
        if serializer.data:
            return Response({'msg': 'Success','data':serializer.data},status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

    # TO MAKE RETAILER INACTIVE
    @transaction.atomic 
    def put(self, request, format=None):
        result={}
        user_data = User.getUserById(self,userid=request.data['data']['id'])
        serializer = UserSerialzer(user_data, data={'is_active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 




def generateCardNumber(self,userid,balance):
        result={}
        card_no = cardgen()
        while  Card.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        # print('request.data',request.data)
        # data = request.data['data']
        # print(data)
        if userid:
            u = User.objects.get(id=userid)
            card = Card(user=u,card_number=card_no,is_active=True,balance=balance)
            card.save()
            print(card.card_number,'card_number')
            result['msg'] = "Card Save Successfully"
            result['card_id'] = card.id
        else:
            result['msg'] = "Error Generating Card"

        return card.id
        # return Response({'msg': 'Success'},status=HTTP_200_OK)


