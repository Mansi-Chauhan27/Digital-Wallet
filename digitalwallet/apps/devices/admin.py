from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin
from .models import DeviceAPIKey

@admin.register(DeviceAPIKey)
class DeviceAPIKeyModelAdmin(APIKeyModelAdmin):
    # print(*APIKeyModelAdmin.list_display)
    # list_display = [*APIKeyModelAdmin.list_display, "devices__name"]
    # search_fields = [*APIKeyModelAdmin.search_fields, "devices__name"]
    pass