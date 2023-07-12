from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.serializers import LoginSerializer, RegisterSerializer
from core.user.models import User


class LoginViewset(ModelViewSet, TokenObtainPairView):
    """
    create:
    Logging in the user and return their JWT token pair
    """

    serialize_classes = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])
            
            user = User.objects.get(username=request.data['username'])
            update_last_login(None, user)
            user_info = {
                "user":{"id": user.id, "username": user.username, "last_login": user.last_login},
                "access": serializer.validated_data['access'],
                "refresh": serializer.validated_data['refresh'],
            }
            return Response(user_info, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RegisterViewSet(ModelViewSet, TokenObtainPairView):
    """
    create:
    Register a new user by providing username and password. Return user information and a pair of JWT token
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_is_exists = User.objects.filter(username=serializer.validated_data['username']).exists()
            assert not user_is_exists, 'User already exists'
            
            serializer.save()
            return Response({"detail": "User registration is successfull"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RefreshViewSet(ViewSet, TokenRefreshView):
    """
    create:
    Obtain a new access token from refresh token
    """
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])

            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
