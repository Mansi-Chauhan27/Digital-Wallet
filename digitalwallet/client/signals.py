# code
from django.db.models.signals import post_save, pre_delete
from django.core.signals import request_finished
# from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import User
from django.conf import settings
from django.db.models import Q
# from client.views import generateCardNumber
from common.helper.utils import generateCardNumber
from client.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# to generate card number as customer/admin signs up

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def generate_card(sender, instance=None, created=False, **kwargs):
    if created:
        user = list(User.objects.filter(email=instance).values('id','groups__name','is_admin','is_customer'))
        # gr = user.groups.filter(name='owner').exists()
        if(user[0]['is_admin']==True):
            generateCardNumber(userid=user[0]['id'],balance=100000)
        elif(user[0]['is_customer']==True):
            generateCardNumber(userid=user[0]['id'],balance=0)
        
        # Token.objects.create(user=instance)

    