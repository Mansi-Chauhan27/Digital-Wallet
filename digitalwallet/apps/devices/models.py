from client.models import User
from transaction.models import Card
from django.db import models
from django.db.models import Q

from rest_framework_api_key.models import AbstractAPIKey


class Device(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        null=True,blank=True
    )
   

    class Meta:
        db_table = "devices"
        verbose_name = "Devices"
        managed  = True

    def getDevices(self):
        return list(Device.objects.filter(~Q(card=None),active=True).values('card__id','name','active'))

    def getAllDevices(self):
        return list(Device.objects.all().values('id','name','card__id'))

    def getDevicesById(self,deviceid):
        return Device.objects.get(id=deviceid)

    def getDeviceByRetailer(self,userid):
        return list(Device.objects.filter(user_id=userid).values('name','active','id','api_keys__id').all())

class DeviceAPIKey(AbstractAPIKey):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Device API key"
        verbose_name_plural = "Device API keys"
        db_table = "devices_api_keys"
        managed  = True

    def getDeviceApiKeyById(self,deviceid):
        return DeviceAPIKey.objects.filter(device_id=deviceid)

    def getAllDeviceApiKey(self):
        return DeviceAPIKey.objects.all()

# class DeviceAPIKeyManager(BaseAPIKeyManager):
#     def get_usable_keys(self):
#         return super().get_usable_keys().filter(organization__active=True)
