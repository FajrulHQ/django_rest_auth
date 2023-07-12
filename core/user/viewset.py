from django.shortcuts import get_object_or_404
from rest_framework import filters, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from core.user.models import User
from core.user.serializers import ManageUserSerializer, UserSerializer

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    list:
    Return list of active users

    read:
    Return user details for the corresponding Id
    """
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
class ManageUserViewset(viewsets.ModelViewSet):
    """
    create:
    Add or remove user after login by username and password
    """
    serializer_class = ManageUserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            action = serializer.validated_data['action']

            user = User.objects.get(username=request.user.username)
            if action == 'add':
                add_user_is_exists = User.objects.filter(username=username).exists()
                if not user.is_staff:
                    return Response({"detail": "Authentication credentials were not provided"}, status=status.HTTP_401_UNAUTHORIZED)
                assert not add_user_is_exists, 'User already exists'
                
                User.objects.create_user(username=username, password=password)
                return Response({"detail": f"{username} registration is successfull"}, status=status.HTTP_201_CREATED)
            
            elif action == 'remove':
                assert request.user.username == username, 'username incompatible'
                assert user.check_password(password), 'password incorrect'
                
                user.delete()
                return Response({"detail": f"{username} removed successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    