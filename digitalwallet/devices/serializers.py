from django.db.models import fields
from rest_framework import serializers
# from django.contrib.auth.models import Token
from .models import Device, DeviceAPIKey
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from client.tasks import send_mail_task
from rest_framework.authtoken.models import Token



class DeviceSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class DeviceAPIKeySerialzer(serializers.ModelSerializer):
    class Meta:
        model = DeviceAPIKey
        fields = '__all__'


