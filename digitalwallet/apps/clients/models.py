import random as r
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

from apps.clients.managers import UserManager



class User(AbstractUser):
    
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = None
    is_customer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Users"

    def get_user_email_by_id(self,userid):
        return list(User.objects.filter(id=userid).values('email'))[0]['email']

    def get_user_by_id(self,userid):
        return User.objects.get(id=userid)

    def get_user_by_email(self,email):
        return User.objects.get(email=email)

    def get_all_users(self):
        return User.objects.all()

    def get_all_customers(self):
        return User.objects.filter(is_customer=True).all()

    def get_all_retailers(self):
        return User.objects.filter(~Q(email='AnonymousUser'),is_customer=False,is_admin=False,is_superuser=False).all()

    def get_group_by_name(self,name):
        return Group.objects.get(name=name)

############# ACCORDING TO NEW DB SCHEMA ################

class Otp(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_id",
    )
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "otps"
        verbose_name = "Otps"
        managed  = True


    def get_latest_otp_of_user(self,user_id):
        return Otp.objects.filter(user_id=user_id).order_by('-created_at').first()

    def get_otp_id(self,otp):
        return Otp.objects.get(otp=otp)

    def generate_otp(self):
        otp=""
        for i in range(4):
            otp+=str(r.randint(1,9))
        return otp


############# ACCORDING TO OLD SCHEMA ################


# OLD
class RegisterUserOtp(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    otp = models.IntegerField()
    expiry = models.DateTimeField(default=datetime.now()+timedelta(hours=2))

# OLD
class VerifyUserOtp(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    otp = models.IntegerField()
    expiry = models.DateTimeField(default=datetime.now()+timedelta(hours=2))
