
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
from rest_framework.views import APIView
# from django.contrib.auth.models import User
from .serializers import DeviceSerialzer, DeviceAPIKeySerialzer
from rest_framework import generics, serializers
from apps.devices.models import Device, DeviceAPIKey
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from client.decorators import admin_required, group_required
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm
from rest_framework.permissions import IsAuthenticated
from client.views import generateCardNumber
from transaction.models import Card
# from rest_framework_api_key.models import APIKey
from braces.views import GroupRequiredMixin
from django.db import transaction



# to get/add/deactivate devices
class DeviceDetails(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')
    #required
    group_required = ["owner","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # @method_decorator(group_required('admin'))
    def get(self,request):
        result={}
        userid= request.user.id
        # userid= 66
        queryset = Device.objects.all()
        # print(queryset,'uhiuhu')
        # print('queryset',Device.objects.filter(user_id=userid).values('name','active','id','api_keys__id'))
        serializer = DeviceSerialzer(queryset, many=True)
        # print(serializer.data)
        result['data'] = serializer.data
        # result['data'] = list(Device.objects.filter(user_id=userid).values('name','active','id','api_keys__id').all())
        result['data'] = Device.getDeviceByRetailer(self,userid)
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

    # Add a device
    # @method_decorator(group_required('admin'))
    @transaction.atomic 
    def post(self,request):
        result={}
        # data will contain giftcard
        data=request.data['data']
        device_data  = {'name':data['device_name'],'is_active':False,'user':request.user.id}

        device_serializer = DeviceSerialzer(data = device_data)
        print('serializer',device_serializer)
        try:
            if device_serializer.is_valid(raise_exception=True):
                trans = device_serializer.save()
                # print('balance',balance)
                cardid = generateCardNumber(self,request.user.id,balance=0)
                print('datadata',cardid)
                Device.objects.filter(id=trans.id).update(card=cardid)
                # result['data']=trans

            
        except Exception as e:
            print(e)
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)


    # @method_decorator(group_required('admin'))
    @transaction.atomic 
    def put(self, request, format=None):
        result={}
        print(request.data,'huijoijoi')
        # user_data = Device.objects.get(id=request.data['data']['id'])
        user_data = Device.getDevicesById(self,deviceid=request.data['data']['id'])
        print(request.user,'uyiuyi')
        serializer = DeviceSerialzer(user_data, data={'active': False}, partial=True)

        if serializer.is_valid():
            serializer.save()
            result['msg']='Success'
            # device_api_key = DeviceAPIKey.objects.filter(device_id=request.data['data']['id'])
            device_api_key = DeviceAPIKey.getDeviceApiKeyById(self,deviceid=request.data['data']['id'])
            if device_api_key:
                device_api_key.update(revoked=True)
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            result['msg']='Error'
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 

# to generate device key
class DeviceApiKeyDetails(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    print('sdafdas')
    #required
    group_required = ["owner","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    # @method_decorator(group_required('admin'))
    def get(self,request):
        result={}
        queryset = DeviceAPIKey.getAllDeviceApiKey(self)
        serializer = DeviceAPIKeySerialzer(queryset, many=True)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

    


    # to generate key
    # @method_decorator(group_required('owner'))
    @transaction.atomic 
    def post(self,request):
        result={}
        # data will contain giftcard
        print(request.user,'huihiuhuiu')
        data=request.data['data']
        # device_api_key_data  = {'name':'apikey','device':2,}

        # device_api_key_serializer = DeviceAPIKeySerialzer(data = device_api_key_data)
        # print('serializer',device_api_key_serializer)
        try:
            # if device_api_key_serializer.is_valid(raise_exception=True):
            #     trans = device_api_key_serializer.save()
            #     # print('balance',balance)
            #     result['data':trans]

            # api_key, key = DeviceAPIKey.objects.create_key(name="apikey",device=Device.objects.get(id=data['device_id']))
            api_key, key = DeviceAPIKey.objects.create_key(name="apikey",device=Device.getDevicesById(self,deviceid=data['device_id']))

            print(api_key,'keyyy',key)
            result['data']=key
            if key:
                Device.objects.filter(id=data['device_id']).update(active=True)
        except Exception as e:
            print(e)
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        # return Response({'msg': 'Success'},status=HTTP_200_OK)

