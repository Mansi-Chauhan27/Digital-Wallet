from django.urls import path

from . import views

urlpatterns = [
    path('getbalance/', views.GetBalance.as_view(), name='getbalance'),
    path('transfermoney/', views.TransferMoney.as_view(), name='transfermoney'),
    path('getcards/', views.GetCards.as_view(), name='getcards'),
    path('transactiondetail/', views.Transaction1.as_view(), name='transaction'),
    path('pdf/', views.GeneratePdf.as_view()),
]