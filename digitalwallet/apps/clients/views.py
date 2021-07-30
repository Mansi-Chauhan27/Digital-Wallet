import re
from datetime import datetime, timedelta

from braces.views import GroupRequiredMixin
from dateutil import parser
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from guardian.shortcuts import assign_perm
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED)
from rest_framework.views import APIView

from apps.clients.decorators import group_required
from apps.clients.tasks import send_mail_task2
from apps.common.helper.utils import cardgen
from apps.transactions.models import Card

from .models import Otp, User
from .serializers import OtpSerialzer, RegisterSerializer, UserSerialzer

'''
    USER REGISTRATION

'''
class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @transaction.atomic 
    def post(self, request, *args, **kwargs):
    # try:
        serializer =  self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        
        user_type=None
        user_type = 'admin' if request.data['is_admin']=='True' else 'customer' if request.data['is_customer']=='True' else 'owner'
        if user_type:
            my_group = User.get_group_by_name(self,user_type)
            my_group.user_set.add(user)
        
        return Response({
            "token":Token.objects.get(user=user).key,'msg':'Success','is_admin':request.data['is_admin'], 'user_type':user_type,'user_id':user.id, 'is_verified':user.is_verified
        },status=HTTP_201_CREATED)
    
    

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
        return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin, 'user_type':user_type, 'user_id':user.id ,'is_verified':user.is_verified},
                        status=HTTP_200_OK)
    # else:
    #     return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
    #                     status=HTTP_200_OK)


'''
    FOR OTP GENERATION AND VERIFICATION

'''
class OtpView(APIView):
    permission_classes = (IsAuthenticated,)
    
    # generate
    def get(self,request):

        user_id = request.user.id
        email_id = request.user.email
        if user_id is None:
            return Response({'error': 'Please provide otp'},
                            status=HTTP_400_BAD_REQUEST)
        
        else:
            otp=Otp.generate_otp(self)
            send_mail_task2.delay(user_id,otp,email_id,settings.SENDER_EMAIL,settings.SENDGRID_KEY)
            otp_data  = {
                        'user':user_id,
                        'otp': otp,
                        'is_used':False,
                        }
            otp_serializer = OtpSerialzer(data = otp_data)
            otp_serializer.is_valid()
            if otp_serializer.is_valid(raise_exception=True):
                otp_serializer.save()
            # user = Otp(user_id=userid,otp=otp,is_used=False)
            # user.save()
            return Response({'msg': 'Otp Send Successfully'},status=HTTP_201_CREATED)
    
    # verify
    
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
                user_data = User.get_user_by_id(self,userid=request.user.id)
                user_serializer = UserSerialzer(user_data, data={'is_verified': True}, partial=True)

                otp_data = Otp.get_otp_id(self,int(otp))
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
        
        
'''
    CUSTOMERS

'''
class Customers(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = "admin"
    raise_exception = True
    redirect_unauthenticated_users = False

    # TO GET ALL THE CUSTOMERS
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
        user_data = User.get_user_by_id(self,userid=request.data['data']['id'])
        serializer = UserSerialzer(user_data, data={'is_active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 


'''
    OWNERS/RETAILERS

'''
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
        user_data = User.get_user_by_id(self,userid=request.data['data']['id'])
        serializer = UserSerialzer(user_data, data={'is_active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 


class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
