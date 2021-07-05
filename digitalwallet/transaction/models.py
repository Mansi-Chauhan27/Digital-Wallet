# from digitalwallet.digitalwallet.settings import AUTH_USER_MODEL
from django.db import models
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from client.models import User
from devices.models import Device

# Create your models here.




class CardDetails(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        # primary_key=True,
    )
    card_number = models.IntegerField()
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
    
class GiftCard(models.Model):
    gift_card_no = models.CharField(max_length=32)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    # user = models.ManyToManyField(User)

    class Meta:
        managed = True

class TransactionDetails(models.Model):
    balance = models.IntegerField()
    credit_amount = models.IntegerField()
    debit_amount = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    is_topup = models.BooleanField(default=False)
    card = models.ManyToManyField(CardDetails)
    gift_card = models.ForeignKey(GiftCard, null=True, blank=True, on_delete=models.CASCADE,)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE,)


    class Meta:
        managed = True



class Task(models.Model):
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('assign_task', 'Assign task'),
        )
    

    

