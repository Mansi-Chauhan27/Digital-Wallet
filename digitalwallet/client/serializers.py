from django.db.models import fields
from rest_framework import serializers
# from django.contrib.auth.models import Token
from .models import User, RegisterUserOtp, Otp
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from client.tasks import send_mail_task, send_mail_task2
from rest_framework.authtoken.models import Token


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
        print('validated_data',validated_data)
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
        print('user.id',user.id)
        send_mail_task2.delay(user.id)
        token=Token.objects.get(user=user).key
        print('token',token)
        # data={'token':}
        print(user)
        return user

    # def get_auth_token(self, obj):
        
    #     token = Token.objects.get(user=user).key
    #     return token

    



class RegisterUserOtpSerialzer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUserOtp
        fields = '__all__'

class OtpSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'


class UserSerialzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(UserSerialzer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        print('this - here',instance)
        demo = User.objects.get(pk=instance.id)
        User.objects.filter(pk=instance.id)\
                           .update(**validated_data)
        return demo
