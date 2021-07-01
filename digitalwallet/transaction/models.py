# from digitalwallet.digitalwallet.settings import AUTH_USER_MODEL
from django.db import models
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from client.models import User

# Create your models here.




class CardDetails(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    card_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)



class Task(models.Model):
    summary = models.CharField(max_length=32)
    content = models.TextField()
    # reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('assign_task', 'Assign task'),
        )
    

    

