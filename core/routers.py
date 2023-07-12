from rest_framework.routers import SimpleRouter
from core.auth.viewset import LoginViewset, RegisterViewSet, RefreshViewSet
from core.user.viewset import UserViewSet, ManageUserViewset
routes = SimpleRouter()

# AUTH
routes.register(r'auth/login', LoginViewset, basename='auth-login')
routes.register(r'auth/register', RegisterViewSet, basename='auth-register')
routes.register(r'auth/refresh', RefreshViewSet, basename='auth-refresh')

# USER
routes.register(r'user/list', UserViewSet, basename='user')
routes.register(r'user/manage', ManageUserViewset, basename='user-manage')
