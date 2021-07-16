from django.conf import settings
from django.core.signals import request_finished
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# from apps.common.helper.utils import generateCardNumber
from apps.clients.models import Token, User
from apps.clients.serializers import UserSerialzer
from apps.transactions.models import Card


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


'''
    to generate card number as customer/admin signs up
    
'''

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def generate_card(sender, instance=None, created=False, **kwargs):
    card = Card()
    user = User()
    if created:
        user_data = user.get_user_by_email(instance)
        user_serializer = UserSerialzer(user_data)
        if(user_serializer.data['is_admin']==True):
            card.generate_card_number(user_serializer.data['id'],balance=100000)
        elif(user_serializer.data['is_customer']==True):
            card.generate_card_number(user_serializer.data['id'],balance=0)
            