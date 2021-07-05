from django.urls import path

from . import views

urlpatterns = [
    path('devices/', views.DeviceDetails.as_view(), name='devices'),
    path('devicekey/', views.DeviceApiKeyDetails.as_view(), name='devicekey'),
]