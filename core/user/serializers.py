from core.user.models import User
from rest_framework import serializers
from django.core.validators import RegexValidator

usernameValidator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Username should be alphanumeric only.')

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'created', 'updated', 'last_login', 'is_superuser']
        read_only_field = ['created', 'updated']

class ManageUserSerializer(serializers.Serializer):
    ACTION_CHOICES = (
        ('add'),
        ('remove'),
    )
    username = serializers.CharField(max_length=20, min_length=6, write_only=True, required=True,
                                     help_text="User's username to be registered", validators=[usernameValidator])
    password = serializers.CharField(max_length=20, min_length=6, write_only=True, required=True,
                                     help_text="User's password for credential")
    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True,
                                     help_text="Choose to add or remove user account")
    class Meta:
        fields = '__all__'