from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.clients.models import User
from apps.common.helper.utils import cardgen


########## According to New db Schema ###############

class Card(models.Model):
    card_number = models.IntegerField(unique=True)
    balance = models.IntegerField(default=0)
    user = models.ForeignKey(
        User,
        related_name='cards_detail',
        on_delete=models.CASCADE,
        null=True,blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "cards"
        verbose_name = "Cards"
        managed  = True

    def get_users_cards(self,userid):
        return Card.objects.filter(user=userid)

    def get_card_by_id(self,card_id):
        return Card.objects.get(id=card_id)

    def get_other_users_cards(self,user_id):
        return Card.objects.filter(~Q(user=user_id))

    def get_users_cards_for_refund(self,device_card_list):
        return Card.objects.filter(~Q(id__in = device_card_list))
    
    def generate_card_number(self,user_id,balance):
        result={}
        card_no = cardgen()
        while  Card.objects.filter(card_number=int(card_no)) :
            card_no = cardgen()

        if user_id:
            u = User.objects.get(id=user_id)
            card = Card(user=u,card_number=card_no,is_active=True,balance=balance)
            card.save()
            result['msg'] = "Card Save Successfully"
            result['card_id'] = card.id
        else:
            result['msg'] = "Error Generating Card"

        return card.id


class Transaction(models.Model):
    amount = models.IntegerField()
    from_card = models.ForeignKey(Card, on_delete=models.CASCADE,related_name='from_card',null=True,blank=True)
    to_card = models.ForeignKey(Card, on_delete=models.CASCADE,related_name='to_card',null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True,blank=True)


    class Meta:
        db_table = "transactions"
        verbose_name = "Transactions"
        managed = True


    def get_transactions(self,card_id):
        return Transaction.objects.filter(Q(to_card = card_id)|Q(from_card = card_id)).all()

########## According to previous db Schema ###############

# OLD
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

# OLD   
class GiftCard(models.Model):
    gift_card_no = models.CharField(max_length=32)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    # user = models.ManyToManyField(User)

    class Meta:
        managed = True

# OLD
class TransactionDetails(models.Model):
    balance = models.IntegerField()
    credit_amount = models.IntegerField()
    debit_amount = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    is_topup = models.BooleanField(default=False)
    card = models.ManyToManyField(CardDetails)
    gift_card = models.ForeignKey(GiftCard, null=True, blank=True, on_delete=models.CASCADE,)
    # device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE,)


    class Meta:
        managed = True


    
# DJANGO GUARDIAN TEST
class Task(models.Model):
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('assign_task', 'Assign task'),
        )
    

    
