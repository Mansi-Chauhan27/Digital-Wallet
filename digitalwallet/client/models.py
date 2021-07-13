# from digitalwallet.digitalwallet.settings import AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from datetime import datetime, timedelta
from django.db.models import Q
# import client.views 
# Create your models here.



class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)



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

    def getUserEmailById(self,userid):
        return list(User.objects.filter(id=userid).values('email'))[0]['email']

    def getUserById(self,userid):
        return User.objects.get(id=userid)


    def getAllCustomers(self):
        return list(User.objects.filter(is_customer=True).values('id','first_name','last_name','email','is_active','carddetails__id'))

    def getAllRetailers(self):
        return list(User.objects.filter(is_customer=False,is_admin=False).values('id','first_name','last_name','email','is_active','carddetails__id'))


class RegisterUserOtp(models.Model):
    
    # email = models.EmailField(
    #     verbose_name='email address',
    #     max_length=255,
    #     unique=True,
    # )
    # username = None
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    otp = models.IntegerField()
    expiry = models.DateTimeField(default=datetime.now()+timedelta(hours=2))


class VerifyUserOtp(models.Model):
    
    # email = models.EmailField(
    #     verbose_name='email address',
    #     max_length=255,
    #     unique=True,
    # )
    # username = None
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    otp = models.IntegerField()
    expiry = models.DateTimeField(default=datetime.now()+timedelta(hours=2))

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

    def getOtpByUserId(self,userid):
        return list(Otp.objects.filter(user_id=userid).order_by('-created_at').values())



    

