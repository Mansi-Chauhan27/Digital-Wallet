from client.models import User
from transaction.models import Card
from django.db import models

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
        managed  = True

class DeviceAPIKey(AbstractAPIKey):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Device API key"
        verbose_name_plural = "Device API keys"
        db_table = "devices_api_key"
        managed  = True


# class DeviceAPIKeyManager(BaseAPIKeyManager):
#     def get_usable_keys(self):
#         return super().get_usable_keys().filter(organization__active=True)
