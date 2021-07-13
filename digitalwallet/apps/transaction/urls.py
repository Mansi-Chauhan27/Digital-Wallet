from django.urls import path

from . import views

urlpatterns = [
    path('generatecard/', views.GenerateCardNumber.as_view(), name='generatecard'),
    path('transactiondetail/', views.Transaction1.as_view(), name='transaction'),
    path('giftcardredeem/', views.GiftCardTopup.as_view(), name='giftcardredeem'),
    path('giftcard/', views.GiftCardTransaction.as_view(), name='giftcard'),
    path('getbalance/', views.GetBalance.as_view(), name='getbalance'),
    path('transfermoney/', views.TransferMoney.as_view(), name='transfermoney'),
    path('getcards/', views.GetCards.as_view(), name='getcards'),
]