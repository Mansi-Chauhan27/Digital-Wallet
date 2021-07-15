
# from rest_framework_api_key.models import APIKey
from braces.views import GroupRequiredMixin
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from rest_framework.views import APIView

# from apps.clients.views import generateCardNumber
from apps.devices.models import Device, DeviceAPIKey
from apps.transactions.models import Card

# from django.contrib.auth.models import User
from .serializers import DeviceAPIKeySerialzer, DeviceSerialzer


# to get/add/deactivate devices   generate card no add?
class DeviceDetails(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = ["owner","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False

    # To Get All The Devices
    def get(self,request):
        result={}
        user_id= request.user.id
        queryset = Device.get_all_devices_of_reatiler(self,user_id)
        serializer = DeviceSerialzer(queryset, many=True)
        result['data'] = serializer.data
        if serializer.data:
            return Response({'msg': 'Success','data':result},status=HTTP_200_OK)
        else:
            return Response(HTTP_404_NOT_FOUND)

    # To Add a device
    @transaction.atomic 
    def post(self,request):
        result={}
        data=request.data['data']
        device_data  = {'name':data['device_name'],'active':False,'user':request.user.id}

        device_serializer = DeviceSerialzer(data = device_data)
        if device_serializer.is_valid(raise_exception=True):
            trans = device_serializer.save()
            card_id = Card.generate_card_number(self,request.user.id,balance=0)
            device_data = Device.get_device_by_id(self,trans.id)
            serializer = DeviceSerialzer(device_data, data={'card': card_id}, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({},status = HTTP_200_OK) 
            else:
                return Response({},status = HTTP_400_BAD_REQUEST) 
      
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

    # To Deactivate the Device
    @transaction.atomic 
    def put(self, request, format=None):
        result={}
        device_data = Device.get_device_by_id(self,request.data['data']['id'])
        serializer = DeviceSerialzer(device_data, data={'active': False}, partial=True)
        if serializer.is_valid():
            serializer.save()
            device_api_key_data = DeviceAPIKey.get_device_apikey(self,request.data['data']['id'])
            if(device_api_key_data):
                device_api_key_serializer = DeviceAPIKeySerialzer(device_api_key_data, data={'revoked':True},partial=True)
                if device_api_key_serializer.is_valid():
                    device_api_key_serializer.save()
            return Response({'data':result}, status = HTTP_200_OK) 
        else:
            return Response({'data':result}, status = HTTP_400_BAD_REQUEST) 

# to generate device key
class DeviceApiKeyDetails(GroupRequiredMixin,APIView):
    permission_classes = (IsAuthenticated,)
    #required
    group_required = ["owner","admin"]
    raise_exception = True
    redirect_unauthenticated_users = False


    def get(self,request):
        result={}
        queryset = DeviceAPIKey.get_all_deviceapikey(self)
        serializer = DeviceAPIKeySerialzer(queryset, many=True)
        result['data'] = serializer.data
        return Response({'msg': 'Success','data':result},status=HTTP_200_OK)

    
    # to generate key
    @transaction.atomic 
    def post(self,request):
        result={}
        data=request.data['data']
        api_key, key = DeviceAPIKey.objects.create_key(name="apikey",device=Device.get_device_by_id(self,data['device_id']))
        result['data']=key
        if key:
            device_data = Device.get_device_by_id(self,data['device_id'])
            serializer = DeviceSerialzer(device_data, data={'active': True}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':result},status=HTTP_200_OK)
            else:
                return Response({},HTTP_400_BAD_REQUEST)
        else:
            return Response({},HTTP_404_NOT_FOUND)
       
