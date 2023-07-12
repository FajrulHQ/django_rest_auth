from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login

from core.user.serializers import UserSerializer
from core.user.models import User
from django.core.validators import RegexValidator

usernameValidator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Username should be alphanumeric only.')

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['user'] = UserSerializer(self.user).data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
    
class RegisterSerializer(UserSerializer):
    username = serializers.CharField(max_length=20, min_length=6, write_only=True, required=True,
                                     help_text="User's username to be registered", validators=[usernameValidator])
    password = serializers.CharField(max_length=20, min_length=6, write_only=True, required=True,
                                     help_text="User's password for credential")
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    