from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='index'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
]