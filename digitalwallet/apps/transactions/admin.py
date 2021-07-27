from django.contrib import admin
from apps.transactions.models import Transaction, Card

# Register your models here.

admin.site.register([Transaction,Card])
