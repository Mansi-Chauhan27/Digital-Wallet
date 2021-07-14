from django.db.models import fields
from rest_framework import serializers
from .models import User, RegisterUserOtp, Otp
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from apps.client.tasks import send_mail_task, send_mail_task2
from rest_framework.authtoken.models import Token
from apps.common.helper.utils import otpgen
from apps.transaction.serializers import CardSerializer


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
        otp=otpgen()
        send_mail_task2.delay(user.id,otp,user.email)
        token=Token.objects.get(user=user).key
        # Insertion IN OTP Table
        return user



class RegisterUserOtpSerialzer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUserOtp
        fields = '__all__'

class OtpSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['id','user_id','otp','created_at','is_used']

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(OtpSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = Otp.objects.get(pk=instance.id)
        Otp.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo


class UserSerialzer(serializers.ModelSerializer):
    cards = CardSerializer(many=True)
    class Meta:
        model = User
        fields = ('first_name','last_name','email','is_active','cards','is_verified')

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(UserSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        demo = User.objects.get(pk=instance.id)
        User.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo
