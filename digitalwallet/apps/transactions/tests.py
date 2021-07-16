from django.contrib.auth.models import Group
from apps.transactions.models import Card, Transaction
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



class TransactionTestCase(APITestCase):
    def setUp(self):
        call_command('loaddata', 'fixtures/sample_data.json', verbosity=0)
                
        admin = {'first_name': 'test', 'last_name': 'user', 'email': 'admin@gmail.com',
                'is_customer':False, 'is_admin':True,'password':'admin@123','password2':'admin@123','is_owner':False}
        self.client.post('/client/register/',admin)

        customer = {'first_name': 'test', 'last_name': 'user', 'email': 'customer@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False}
        self.client.post('/client/register/',customer)

        User.objects.filter(email='customer@gmail.com').update(is_verified=True)
        User.objects.filter(email='admin@gmail.com').update(is_verified=True)
       
        self.customer = User.objects.get(email='customer@gmail.com')
        self.admin = User.objects.get(email='admin@gmail.com')
        self.token = Token.objects.get(user=self.admin).key
        self.api_authentication()
    
    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_get_all_cards(self):
        data = {
            'data': {'action': 'get_users_cards'}
        }
        res=self.client.post('/transaction/getcards/',data, format='json')
        res2=self.client.post('/transaction/getcards/',{'data':{'action':'get_users_cards_by_id','userid':3}}, format='json')
        res3=self.client.post('/transaction/getcards/',{'data':{'action':'get_other_users_cards'}}, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res2.status_code,status.HTTP_200_OK)
        self.assertEqual(res3.status_code,status.HTTP_200_OK)
        self.assertEqual(Card.objects.count(),2)

    def test_transfer_money_from_customer(self):
        data = {
            'data': {'action': 'from_customer','from_card_id':1,'to_card_id':2,'amount_to_be_transferred':100}
        }
        
        res=self.client.post('/transaction/transfermoney/',data, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Card.objects.filter(id=1).values().first()['balance'],99900)
        self.assertEqual(Card.objects.filter(id=2).values().first()['balance'],100)


    def test_transfer_money_insufficient_balance(self):
        customer = {'first_name': 'test', 'last_name': 'user', 'email': 'customer2@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False,'is_verified':True}
        self.client.post('/client/register/',customer)

        User.objects.filter(email='customer2@gmail.com').update(is_verified=True)
        data = {
            'data': {'action': 'from_customer','from_card_id':2,'to_card_id':3,'amount_to_be_transferred':10}
        }
        
        res=self.client.post('/transaction/transfermoney/',data, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content)['data']['msg'],'Insufficient Balance')
        self.assertEqual(Card.objects.filter(id=2).values().first()['balance'],0)
        self.assertEqual(Card.objects.filter(id=3).values().first()['balance'],0)

    def test_transfer_money_from_customer_from_customer(self):
        data_from_admin = {
            'data': {'action': 'from_customer','from_card_id':1,'to_card_id':2,'amount_to_be_transferred':100}
        }
        
        self.client.post('/transaction/transfermoney/',data_from_admin, format='json')

        # create another customer
        customer = {'first_name': 'test', 'last_name': 'user', 'email': 'customer2@gmail.com',
                'is_customer':True, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':False,'is_verified':True}
        self.client.post('/client/register/',customer)
        
        # Transfer Money to another customer
        data_from_customer = {
            'data': {'action': 'from_customer','from_card_id':2,'to_card_id':3,'amount_to_be_transferred':10}
        }
        
        res=self.client.post('/transaction/transfermoney/',data_from_customer, format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Card.objects.filter(id=2).values().first()['balance'],90)
        self.assertEqual(Card.objects.filter(id=3).values().first()['balance'],10)



    def test_transfer_money_to_device(self):
        # create retailer
        owner = {'first_name': 'test', 'last_name': 'user', 'email': 'retailer@gmail.com',
                'is_customer':False, 'is_admin':False,'password':'admin@123','password2':'admin@123','is_owner':True,'is_verified':True}
        self.client.post('/client/register/',owner)

        User.objects.filter(email='retailer@gmail.com').update(is_verified=True)
        self.token = Token.objects.get(user=User.objects.get(email='retailer@gmail.com')).key
        self.api_authentication()
        # Add Device
        data = {
            'data': {'device_name': 'dominos'}
        }
        res=self.client.post('/devices/devices/',data, format='json')
        
        # Generate Device Apikey
        device_data = {
            'data': { 'device_id': 1 }
        }
        res_key=self.client.post('/devices/devicekey/',device_data, format='json')

        # Transfer Money from admin to customer
        data_from_admin = {
            'data': {'action': 'from_customer','from_card_id':1,'to_card_id':2,'amount_to_be_transferred':100}
        }
        
        self.client.post('/transaction/transfermoney/',data_from_admin, format='json')

        # Transfer Money from customer to device
        self.token = Token.objects.get(user=self.customer).key
        self.api_authentication()
        data_from_customer_to_device = {
            'data': {'action': 'from_customer','from_card_id':2,'to_card_id':3,'amount_to_be_transferred':20}
        }
        
        res=self.client.post('/transaction/transfermoney/',data_from_customer_to_device, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Card.objects.filter(id=2).values().first()['balance'],80)
        self.assertEqual(Card.objects.filter(id=3).values().first()['balance'],20)

        # Check Balance
        self.token = Token.objects.get(user=self.customer).key
        self.api_authentication()
        res=self.client.post('/transaction/getbalance/',{'data':{'action':'get_balance'}}, format='json')
        self.assertEqual(len(json.loads(res.content)['data']['data']),1)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

        # Check History
        
        res=self.client.post('/transaction/getbalance/',{'data':{'action':'get_history','card_id':2}}, format='json')
        self.assertEqual(len(json.loads(res.content)['data']['data']),2)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

        # Refund Transaction
        self.token = Token.objects.get(user=User.objects.get(email='retailer@gmail.com')).key
        self.api_authentication()
        data_from_device_from_customer = {
            'data': {'action': 'from_device','device_id':1,'from_card_id':3,'to_card_id':2,'amount_to_be_transferred':10}
        }
        
        res=self.client.post('/transaction/transfermoney/',data_from_device_from_customer, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(Card.objects.filter(id=2).values().first()['balance'],90)
        self.assertEqual(Card.objects.filter(id=3).values().first()['balance'],10)
