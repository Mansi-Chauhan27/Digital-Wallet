from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='index'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('otp/', views.otpgen, name='otp'),
    path('verifyotp/', views.verifyotp, name='verifyotp'),
    path('getcustomers/', views.getCustomers, name='getcustomers'),
]