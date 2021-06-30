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
from .serializers import RegisterSerializer
from rest_framework import generics, serializers
from .models import User, RegisterUser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from client.decorators import admin_required
from rest_framework.authtoken.models import Token


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     print('queryset',queryset)
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer

#     print(serializer_class.data)
    

class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    print('queryset',queryset)
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


    def post(self, request, *args, **kwargs):
        serializer =  self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        print('erfsdfsdf',user)
        return Response({
            "token":Token.objects.get(user=user).key
        })
    # print(serializer_class.data)
    
    


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    # username = request.data.get("username")
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
    return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
                    status=HTTP_200_OK)


@csrf_exempt
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
    
    print(list(RegisterUser.objects.filter(user_id=request.user.id).values()))
    user = list(RegisterUser.objects.filter(user_id=request.user.id).values())
    # qs_json = serializers.serialize('json', RegisterUser.objects.filter(user_id=request.user.id).all())
    
    # print(qs_json)
    if user:
        print('uiui')
        print(type(user[0]['otp']))
        print(type(otp))
        if(user[0]['otp']==int(otp)):
            print('tyfyt')
            User.objects.filter(id=request.user.id).update(is_verified=True)
            RegisterUser.objects.filter(user_id=request.user.id).delete()
            return Response({'succes': 'Verified'},status=HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Otp'},status=HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'User Already Verified'},status=HTTP_404_NOT_FOUND)
    #     return Response({'error': 'Invalid Credentials'},
    #                     status=HTTP_404_NOT_FOUND)
    # token, _ = Token.objects.get_or_create(user=user)
    # return Response({'token': token.key,'email':user.email,'is_admin':user.is_admin},
    #                 status=HTTP_200_OK)
    
@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
@login_required
@admin_required
def getCustomers(request):
    print('gygy',request.user.is_admin,request.user)
    user_list = list(User.objects.filter(is_customer=True).values())
    print('efwf')
    return Response({'msg': 'Success','data':user_list},status=HTTP_200_OK)




# @csrf_exempt
# @api_view(["POST"])
# @permission_classes((AllowAny,))
# def signup(request):
#     username = request.data.get("username")
#     password = request.data.get("password")
#     if username is None or password is None:
#         return Response({'error': 'Please provide both username and password'},
#                         status=HTTP_400_BAD_REQUEST)
#     # user = authenticate(username=username, password=password)
#     # if not user:
#     #     return Response({'error': 'Invalid Credentials'},
#     #                     status=HTTP_404_NOT_FOUND)
#     token, _ = Token.objects.get_or_create(user=user)
#     return Response({'token': token.key},
#                     status=HTTP_200_OK)


import random as r
# function for otp generation
@method_decorator([login_required, admin_required], name='dispatch')
def otpgen(request):
    print(request.user)
    otp=""
    for i in range(4):
        otp+=str(r.randint(1,9))
    print ("Your One Time Password is ")
    print (otp)

# otpgen()