from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.clients.models import User




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


class Card(models.Model):
    card_number = models.IntegerField(unique=True)
    balance = models.IntegerField(default=0)
    user = models.ForeignKey(
        User,
        related_name='cards',
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

    def getTransactionDetailsByCardId(self,card_id):
        return list(Transaction.objects.filter(Q(to_card = card_id)|Q(from_card = card_id)).values('id','to_card__card_number','to_card__id','to_card__user_id','from_card__id','from_card__user_id','amount','user__email','from_card__card_number').all())

    def get_transactions(self,card_id):
        return Transaction.objects.filter(Q(to_card = card_id)|Q(from_card = card_id)).all()

    
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
    

    
