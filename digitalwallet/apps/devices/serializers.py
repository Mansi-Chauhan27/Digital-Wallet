from django.db.models import fields
from rest_framework import serializers
# from django.contrib.auth.models import Token
from .models import Device, DeviceAPIKey
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from apps.client.tasks import send_mail_task
from rest_framework.authtoken.models import Token


class DeviceAPIKeySerialzer(serializers.ModelSerializer):
    class Meta:
        model = DeviceAPIKey
        fields = ('id','name','revoked','device_id')

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DeviceAPIKeySerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = DeviceAPIKey.objects.get(pk=instance.id)
        DeviceAPIKey.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo



class DeviceSerialzer(serializers.ModelSerializer):
    api_keys = DeviceAPIKeySerialzer(many=True)
    class Meta:
        model = Device
        # fields = '__all__'
        fields = ('name','active','id','api_keys','user','card')

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DeviceSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = Device.objects.get(pk=instance.id)
        Device.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo


