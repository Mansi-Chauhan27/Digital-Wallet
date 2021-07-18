from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from apps.clients.tasks import send_mail_task, send_mail_task2
from apps.transactions.serializers import CardSerializer

from .models import Otp, RegisterUserOtp, User


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    # token = serializers.SerializerMethodField('get_auth_token')
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'is_admin', 'is_customer')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'is_admin': {'required': True},
            'is_customer': {'required': True},

        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            # username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_admin=validated_data['is_admin'],
            is_customer=validated_data['is_customer'],
            
        )
        # send_mail_task.delay(user.id)
        
        user.set_password(validated_data['password'])
        user.save()
        # generate Otp 
        otp=Otp.generate_otp(self)
        send_mail_task2.delay(user.id,otp,user.email,settings.SENDER_EMAIL,settings.SENDGRID_KEY)
        otp_data  = {
                        'user':user.id,
                        'otp': otp,
                        'is_used':False,
                        }
        otp_serializer = OtpSerialzer(data = otp_data)
        otp_serializer.is_valid()
        if otp_serializer.is_valid(raise_exception=True):
            otp_serializer.save()
        return user


class OtpSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['id','user','otp','created_at','is_used']

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OtpSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = Otp.objects.get(pk=instance.id)
        Otp.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo


class UserSerialzer(serializers.ModelSerializer):
    cards_detail = CardSerializer(many=True)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','is_active','cards_detail','is_verified','is_admin','is_customer']

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(UserSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = User.objects.get(pk=instance.id)
        User.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo
