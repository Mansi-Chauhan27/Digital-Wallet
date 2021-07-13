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
from .serializers import RegisterSerializer, RegisterUserOtpSerialzer, UserSerialzer
from rest_framework import generics, serializers
from .models import User, RegisterUserOtp, Otp
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from transaction.models import CardDetails, Task, Card
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm
from rest_framework.permissions import IsAuthenticated
from datetime import datetime,timedelta
from django.utils import timezone
from client.tasks import send_mail_task, send_mail_task2
from common.helper.utils import cardgen
from django.db.models import Q
from braces.views import GroupRequiredMixin
from django.db import transaction


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     print('queryset',queryset)
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer

#     print(serializer_class.data)
    

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
            print(user,'sdasfsa',my_group)
            user_type='owner'
            my_group.user_set.add(user)

        

        return Response({
            "token":Token.objects.get(user=user).key,'msg':'Success','is_admin':request.data['is_admin'], 'user_type':user_type
        })
        # except Exception as e:
        #     print(e)
        #     return Response({
        #         "msg":str(e)}, status=HTTP_400_BAD_REQUEST)
    # print(serializer_class.data)
    
    

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

# OLD
@api_view(["POST"])
@permission_classes((AllowAny,))
@login_required
def verifyotp(request):
    # username = request.data.get("username")
    otp = request.data.get("otp")
    # password = request.data.get("password")
    if otp is None:
        return Response({'error': 'Please provide otp'},
                        status=HTTP_400_BAD_REQUEST)
    print(request.user)
    print(request.user.id)
    
    print(list(RegisterUserOtp.objects.filter(user_id=request.user.id).values()))
    user = list(RegisterUserOtp.objects.filter(user_id=request.user.id).values())
    # qs_json = serializers.serialize('json', RegisterUserOtp.objects.filter(user_id=request.user.id).all())
    
    # print(qs_json)
    if user:
        print(type(user[0]['otp']))
        print(type(otp))
        print(timezone.now()<user[0]['expiry'])

        if(user[0]['otp']==int(otp) and timezone.now()<user[0]['expiry']):
            print('tyfyt')
            User.objects.filter(id=request.user.id).update(is_verified=True)
            RegisterUserOtp.objects.filter(user_id=request.user.id).delete()
            return Response({'success': 'Verified','msg':'Success'},status=HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Otp','msg':'Error'},status=HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'User Already Verified'},status=HTTP_404_NOT_FOUND)
    #     return Response({'error': 'Invalid Credentials'},
    #                     status=HTTP_404_NOT_FOUND)
    # token, _ = Token.objects.get_or_create(user=user)
    # return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
    #                 status=HTTP_200_OK)

# OLD
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@login_required
def generateOtp(request):
    # username = request.data.get("username")
    user_id = request.user.id
    # password = request.data.get("password")
    if user_id is None:
        return Response({'error': 'Please provide otp'},
                        status=HTTP_400_BAD_REQUEST)
    
    else:
        send_mail_task.delay(user_id)
        return Response({'msg': 'Otp Send Successfully'},status=HTTP_201_CREATED)
    #     return Response({'error': 'Invalid Credentials'},
    #                     status=HTTP_404_NOT_FOUND)
    # token, _ = Token.objects.get_or_create(user=user)
    # return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
    #                 status=HTTP_200_OK)



#  FOR OTP GENERATION AND VERIFICATION
class OtpView(APIView):
    permission_classes = (IsAuthenticated,)
    
    # generate
    def get(self,request):
        print(request.data,'jiujuiju')
        # action='verify'
        # action = request.data['data']['action'] if "action" in request.data else ''
        # print('action',action)
        # action=request.data['data']['action']

        user_id = request.user.id
        if user_id is None:
            return Response({'error': 'Please provide otp'},
                            status=HTTP_400_BAD_REQUEST)
        
        else:
            send_mail_task2.delay(user_id)
            return Response({'msg': 'Otp Send Successfully'},status=HTTP_201_CREATED)
    
    # verify
    
    def post(self,request):
        print(request.data,'jiujuiju')
        # action='verify'
        # action = request.data['data']['action'] if "action" in request.data else ''
        # print('action',action)
        # action=request.data['data']['action']
        otp = request.data.get("otp")
        # password = request.data.get("password")
        if otp is None:
            return Response({'error': 'Please provide otp'},
                            status=HTTP_400_BAD_REQUEST)
        print(request.user)
        print(request.user.id)
        
        # print(list(Otp.objects.filter(user_id=request.user.id).values()))
        # user = list(Otp.objects.filter(user_id=request.user.id).order_by('-created_at').values())
        user = Otp.getOtpByUserId(self,userid=request.user.id)
        # qs_json = serializers.serialize('json', RegisterUserOtp.objects.filter(user_id=request.user.id).all())
        
        # print(qs_json)
        if user:
            print('uiui',user)
            print(type(user[0]['otp']))
            print(type(otp))
            print(timezone.now()<user[0]['created_at']+timedelta(hours=2))

            if(user[0]['otp']==int(otp) and timezone.now()<user[0]['created_at']+timedelta(hours=2)):
                print('tyfyt')
                User.objects.filter(id=request.user.id).update(is_verified=True)
                Otp.objects.filter(otp=int(otp)).update(is_used=True)
                return Response({'success': 'Verified','msg':'Success'},status=HTTP_200_OK)
            else:
                return Response({'error': 'Invalid Otp','msg':'Error'},status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User Already Verified'},status=HTTP_404_NOT_FOUND)
        
       
# ACTIONS ON CUSTOMERS
class Customers(APIView):
    permission_classes = (IsAuthenticated,)
    
    # TO GET ALL THE CUSTOMERS
    @method_decorator(group_required('admin'))
    def get(self, request, *args, **kwargs):
        print('sfs',request.user,request.user.is_admin)
        # print(timezone.now()<list(RegisterUserOtp.objects.filter(user_id=47).values('expiry'))[0]['expiry'])
        # user_list = list(User.objects.filter(is_customer=True).values('id','first_name','last_name','email','is_active','carddetails__id'))
        user_list = User.getAllCustomers(self)
        return Response({'msg': 'Success','data':user_list},status=HTTP_200_OK)

    @method_decorator(group_required('admin'))
    def delete(self, request, *args, **kwargs):
        result={}
        try:
            print('sdsd',request.data)
            u = User.objects.get(username = request.data['id'])
            print(u)
            u.delete()
            result['msg'] = 'User Delete Successfully'

        except User.DoesNotExist:
            result['msg'] = "User doesnot exist"   
            return Response({'msg': 'Success'},status=HTTP_404_NOT_FOUND)

        except Exception as e: 
            return Response({'msg': 'Something Went Wrong!'},status=HTTP_400_BAD_REQUEST)
 
        return Response({'msg': 'Success'},status=HTTP_200_OK)

    # TO MAKE CUSTOMER INACTIVE
    # @method_decorator(group_required('admin'))
    def put(self, request, format=None):
        result={}
        # user_data = User.objects.get(id=request.data['data']['id'])
        user_data = User.getUserById(self,userid=request.data['data']['id'])
        serializer = UserSerialzer(user_data, data={'is_active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 


# Owners
class Owners(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = "admin"
    raise_exception = True
    redirect_unauthenticated_users = False

    # TO GET ALL THE RETAILERS
    # @method_decorator(group_required('admin'))
    def get(self, request, *args, **kwargs):
        print('sfs',request.user,request.user.is_admin)
        print(timezone.now()<list(RegisterUserOtp.objects.filter(user_id=47).values('expiry'))[0]['expiry'])
        # user_list = list(User.objects.filter(is_customer=False,is_admin=False).values('id','first_name','last_name','email','is_active','carddetails__id'))
        user_list = User.getAllRetailers(self)
        return Response({'msg': 'Success','data':user_list},status=HTTP_200_OK)

    # @method_decorator(group_required('admin'))
    def delete(self, request, *args, **kwargs):
        result={}
        try:
            print('sdsd',request.data)
            u = User.objects.get(username = request.data['id'])
            print(u)
            u.delete()
            result['msg'] = 'User Delete Successfully'

        except User.DoesNotExist:
            result['msg'] = "User doesnot exist"   
            return Response({'msg': 'Success'},status=HTTP_404_NOT_FOUND)

        except Exception as e: 
            return Response({'msg': 'Something Went Wrong!'},status=HTTP_400_BAD_REQUEST)
 
        return Response({'msg': 'Success'},status=HTTP_200_OK)

    # TO MAKE RETAILER INACTIVE
    # @method_decorator(group_required('admin'))
    @transaction.atomic 
    def put(self, request, format=None):
        result={}
        # user_data = User.objects.get(id=request.data['data']['id'])
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
        print(userid)
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


