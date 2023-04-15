from rest_framework import serializers, exceptions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from accounts.models import *

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_email = User.objects.filter(email=validated_data['email'])
        if user_email:
            ctx = {
                'status': False,
                'message': "A user with that email already exists."
            }
            return ctx
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        token = self.get_token(user)
        ctx = {
            'user': user.pk,
            'token': token,
            'first_name': user.first_name,
            'email': user.email
        }
        return ctx

    def get_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key
    
class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','groups', 'user_permissions', 'is_superuser', 'username', 'is_staff']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=35)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(
            username=data['email'], password=data['password'])
        if not user:
            raise exceptions.AuthenticationFailed()
        elif not user.is_active:
            raise exceptions.PermissionDenied()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        data['user'] = user
        return data

class UserLoginReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Token
        fields = ('key', 'user')


class RequestDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDonation
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'

class RequestDonationListSerializer(serializers.ModelSerializer):
    donation = DonationSerializer()

    class Meta:
        model = RequestDonation
        exclude = ('created_by', 'updated_by', 'country', 'created_on', 'updated_on', 'state', 'user')