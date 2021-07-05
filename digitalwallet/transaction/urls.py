from django.urls import path

from . import views

urlpatterns = [
    path('generatecard/', views.GenerateCardNumber.as_view(), name='generatecard'),
    path('transactiondetail/', views.Transaction.as_view(), name='transaction'),
    path('giftcardredeem/', views.GiftCardTopup.as_view(), name='giftcardredeem'),
    path('addgiftcard/', views.GiftCardTransaction.as_view(), name='addgiftcard'),
]