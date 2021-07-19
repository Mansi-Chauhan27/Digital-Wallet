from django.contrib.auth.models import Group
from apps.transactions.models import Card
import json

import rest_framework
from apps.clients.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.management import call_command

from apps.clients.serializers import RegisterSerializer
from apps.devices.models import Device
from apps.devices.models import DeviceAPIKey



class DeviceTestCase(APITestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/sample_data.json', verbosity=0)
                
        owner = {'first_name': 'test', 'last_name': 'user', 'email': 'owner@gmail.com',
                'is_customer':False, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':True}
        self.client.post('/client/register/',owner)
        
        User.objects.filter(email='owner@gmail.com').update(is_verified=True)
        self.owner = User.objects.get(email='owner@gmail.com')
        self.token = Token.objects.get(user=self.owner).key
        self.api_authentication()
    
    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_get_all_devices(self):
        res=self.client.get('/devices/devices/')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(),0)

    def test_add_device(self):
        data = {
            'data': {'device_name': 'dominos'}
        }
        res=self.client.post('/devices/devices/',data, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(),1)

    def test_deactivate_device(self):
        data = {
            'data': {'device_name': 'dominos'}
        }
        res=self.client.post('/devices/devices/',data, format='json')

        data_id = {
            'data': { 'id': 1 }
        }
        res=self.client.put('/devices/devices/',data_id, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        # self.assertEqual(User.objects.filter(is_active=False).count(),1)

    def test_generate_api_key(self):
        data = {
            'data': {'device_name': 'dominos'}
        }
        res=self.client.post('/devices/devices/',data, format='json')
        data_id = {
            'data': { 'device_id': 1 }
        }
        res_key=self.client.post('/devices/devicekey/',data_id, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res_key.status_code,status.HTTP_200_OK)
        self.assertEqual(DeviceAPIKey.objects.count(),1)
