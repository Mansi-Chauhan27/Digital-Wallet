from rest_framework import serializers

# from django.contrib.auth.models import Token
from .models import (Card, CardDetails, GiftCard, Transaction,
                     TransactionDetails)



########### ACCORDING TO New DB SCHEMA ########################

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id','card_number','balance','created_at','is_active','user',)


class TransactionSerializer(serializers.ModelSerializer):
    from_card_detail = CardSerializer(source='from_card',read_only=True)
    to_card_detail = CardSerializer(source='to_card',read_only=True)

    class Meta:
        model = Transaction
        fields = ('id','amount','created_at','user','from_card_id','to_card_id','from_card','to_card','from_card_detail','to_card_detail')


########### ACCORDING TO OLD DB SCHEMA ########################

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

 