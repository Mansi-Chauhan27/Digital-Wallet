from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import DeviceAPIKey

class HasDeviceAPIKey(BaseHasAPIKey):
    model = DeviceAPIKey