from django.urls import path

from . import views

urlpatterns = [
    path('generatecard/', views.GenerateCardNumber.as_view(), name='generatecard'),
]