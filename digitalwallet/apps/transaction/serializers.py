from django.db.models import fields
from rest_framework import serializers
# from django.contrib.auth.models import Token
from .models import CardDetails, TransactionDetails, GiftCard, Transaction, Card
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from apps.client.tasks import send_mail_task
from rest_framework.authtoken.models import Token



class CardDetailsSerialzer(serializers.ModelSerializer):
    class Meta:
        model = CardDetails
        fields = '__all__'

    

class TransactionDetailsSerialzer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetails
        fields = '__all__'


class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


