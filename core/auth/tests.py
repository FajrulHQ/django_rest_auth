from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache
from core.auth.serializers import LoginSerializer, RegisterSerializer


# Create your tests here.
class RegisterViewSetTests(APITestCase):
    """
    Test user registration api
    """
    def setUp(self):
        cache.clear()
        self.username = "testuser"
        self.password = "inipassword"

    def test_user_register_success(self):
        url = reverse("auth-register-list")
        register_response = self.client.post(url, dict(username=self.username, password=self.password))
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
    def test_user_register_failed(self):
        url = reverse('auth-register-list')
        register_response = self.client.post(url, dict(password=self.password))
        self.assertEqual(register_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_failed_not_alphanumeric_username(self):
        url = reverse('auth-register-list')
        register_response = self.client.post(url, dict(username=self.username+'/?', password=self.password))
        self.assertEqual(register_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_failed_duplicate(self):
        url = reverse('auth-register-list')
        register_data = dict(username=self.username, password=self.password)
        register_response = self.client.post(url, register_data)
        register_response_duplicate = self.client.post(url, register_data)
        self.assertEqual(register_response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)

class AuthViewSetTests(APITestCase):
    """
    Test user authentication APIs for login (LoginViewSet), and refresh token usage (RefreshViewSet)
    """
    def setUp(self):
        cache.clear()
        self.username = "testuser"
        self.password = "inipassword"

        url = reverse('auth-register-list')
        login_url = reverse('auth-login-list')
        register_data = dict(username=self.username, password=self.password)
        register_response = self.client.post(url, register_data)

        login_data = dict(username=self.username, password=self.password)
        login_response = self.client.post(login_url, login_data)
        self.refresh_token = login_response.data['refresh']
        self.access_token = login_response.data['access']

    def test_user_refresh_success(self):
        url = reverse('auth-refresh-list')
        refresh_response = self.client.post(url, dict(refresh=self.refresh_token))
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

    def test_user_refresh_failed(self):
        url = reverse('auth-refresh-list')
        refresh_response = self.client.post(url, dict(refresh=self.refresh_token+"something"))
        self.assertEqual(refresh_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_refresh_empty(self):
        url = reverse('auth-refresh-list')
        refresh_response = self.client.post(url)
        self.assertEqual(refresh_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        url = reverse('auth-login-list')
        login_response=self.client.post(url, dict(username=self.username, password=self.password))
        self.assertEqual(login_response.status_code, status.HTTP_201_CREATED)

    def test_user_login_failed(self):
        url = reverse('auth-login-list')
        login_response=self.client.post(url, dict(username=self.username, password=self.password+"sometext"))
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthSerializerTestCase(APITestCase):
    """
    Test user authentication serializers for login, register, and refresh
    """
    def setUp(self):
        self.payload = dict(username="testuser", password="inipassword")
        url = reverse('auth-register-list')
        register_response = self.client.post(url, self.payload)

    def test_register_valid_data(self):
        serializer = RegisterSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())
        
    def test_register_missing_required_field(self):
        self.payload.pop('password')
        serializer = RegisterSerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

    def test_login_valid_data(self):
        serializer = LoginSerializer(data=self.payload)
        self.assertTrue(serializer.is_valid())
        
    def test_login_missing_required_field(self):
        self.payload.pop('password')
        serializer = LoginSerializer(data=self.payload)
        self.assertFalse(serializer.is_valid())

class AuthViewSetThrottleTests(APITestCase):
    """
    Test user authentication APIs for login (LoginViewSet) with throttle
    reference: https://stackoverflow.com/questions/39309046/what-is-the-proper-way-of-testing-throttling-in-drf
    """

    def setUp(self):
        self.payload = dict(username="testuser", password="inipassword")

    def test_user_login_throttle(self):
        url = reverse('auth-login-list')
        while(True):
            login_response = self.client.post(url, self.payload)
            if(login_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS):
                break
        self.assertEqual(login_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_register_throttle(self):
        url = reverse('auth-register-list')
        while(True):
            register_response = self.client.post(url, self.payload)
            if(register_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS):
                break
        self.assertEqual(register_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)