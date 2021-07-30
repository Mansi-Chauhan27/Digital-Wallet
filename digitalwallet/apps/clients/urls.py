from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='index'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    # path('otp/', views.otpgen, name='otp'),
    path('verifyotp/', views.OtpView.as_view(), name='verifyotp'),
    path('customers/', views.Customers.as_view(), name='customers'),
    # path('generateotp/', views.generateOtp, name='generateotp'),
    path('owners/', views.Owners.as_view(), name='owners'),
    path('logout/', views.Logout.as_view(), name='logout'),
]