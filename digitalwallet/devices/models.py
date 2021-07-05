from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

class Device(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

class DeviceAPIKey(AbstractAPIKey):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Device API key"
        verbose_name_plural = "Device API keys"


# class DeviceAPIKeyManager(BaseAPIKeyManager):
#     def get_usable_keys(self):
#         return super().get_usable_keys().filter(organization__active=True)
