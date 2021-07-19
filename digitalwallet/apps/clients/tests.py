import json

import rest_framework
from django.contrib.auth.models import Group
from django.core.management import call_command
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.clients.models import User
from apps.clients.serializers import RegisterSerializer
from apps.transactions.models import Card

# Create your tests here.

class RegistrationtestCase(APITestCase):
    # FIXTURE_DIRS = ('/digitalwallet/fixtures/sample_data.json')
    def test_print(self):
        pass
    
    def test_registration(self):
        call_command('loaddata', 'fixtures/sample_data.json', verbosity=0)
        data = {'id':100,'first_name': 'test', 'last_name': 'user', 'email': 'test@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False}
        response  = self.client.post('/client/register/',data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(),1)

class LoginTestCase(APITestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/sample_data.json', verbosity=0)
        customer = {'first_name': 'test', 'last_name': 'user', 'email': 'test2@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False}
        response  = self.client.post('/client/register/',customer)
        self.customer  = User.objects.get(email='test2@gmail.com')
        self.token = Token.objects.get(user=self.customer).key
        self.api_authentication()
    
    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_login_authentication(self):
        res=self.client.post('/client/login/',{'email':self.customer,'password':'admin@123'})
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_login_incorect_credentials(self):
        res=self.client.post('/client/login/',{'email':self.customer,'password':'admin@1234'})
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)


class AdminTestCase(APITestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/sample_data.json', verbosity=0)
        admin = {'first_name': 'test', 'last_name': 'user', 'email': 'admin@gmail.com',
                'is_customer':False, 'is_admin':True,'password':'admin@123','password2':'admin@123','is_owner':False}
        response  = self.client.post('/client/register/',admin)
        customer = {'first_name': 'test', 'last_name': 'user', 'email': 'test2@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False}
        self.client.post('/client/register/',customer)
        
        owner = {'first_name': 'test', 'last_name': 'user', 'email': 'owner@gmail.com',
                'is_customer':False, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':True}
        self.client.post('/client/register/',owner)
        
        self.admin  = User.objects.get(email='admin@gmail.com')
        self.token = Token.objects.get(user=self.admin).key
        self.customer = User.objects.get(email='test2@gmail.com')
        self.owner = User.objects.get(email='owner@gmail.com')
        self.api_authentication()
    
    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_get_all_customers(self):
        res=self.client.get('/client/customers/')
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_deactivate_customer(self):
        data = {
            'data': {'id': self.customer.id}
        }
        res=self.client.put('/client/customers/',data, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(is_active=False,is_customer=True).count(),1)

    def test_get_all_retailer(self):
        res=self.client.get('/client/owners/')
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_deactivate_retailer(self):
        data = {
            'data': {'id': self.owner.id}
        }
        res=self.client.put('/client/owners/',data, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(is_active=False,is_customer=False,is_admin=False).count(),1)
