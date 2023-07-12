from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.user.models import User


# Create your tests here.
class UserListViewSetTests(APITestCase):
    """
    Test user ViewSet, superuser can list all the users both in list or detail view
    and failed for user with is_staff False and unauthenticated
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.superuser = User.objects.create_superuser(username="superuser", password="superpassword")
        self.regular_user = User.objects.create_user(username="testuser", password="inipassword")

    def test_get_user_list_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        user_response = self.client.get(self.url)
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(user_response.data), 2)

    def test_get_user_list_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        user_response = self.client.get(self.url)
        self.assertEqual(user_response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_list_unauthenticated(self):
        user_response = self.client.get(self.url)
        self.assertEqual(user_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_superuser_success(self):
        self.client.force_authenticate(user=self.superuser)
        user_response = self.client.get(reverse('user-detail', kwargs={"pk":2}))
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)

    def test_get_user_detail_superuser_failed(self):
        self.client.force_authenticate(user=self.superuser)
        user_response = self.client.get(reverse('user-detail', kwargs={"pk":3}))
        self.assertEqual(user_response.status_code, status.HTTP_404_NOT_FOUND)

class UserManageViewSetTests(APITestCase):
    """
    Test user-manage ViewSet, superuser can add new user by input username and password
    and also every user can remove account itself by validate username and passowrd
    """

    def setUp(self):
        self.url = reverse('user-manage-list')
        self.superuser = User.objects.create_superuser(username="superuser", password="superpassword")
        self.regular_user = User.objects.create_user(username="testuser", password="inipassword")
        self.add_user = dict(username="adduser", password="userpassword")

    def test_add_user_superuser_success(self):
        self.client.force_authenticate(user=self.superuser)
        self.add_user["action"] = "add"
        add_response = self.client.post(self.url, self.add_user)
        self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)
        
    def test_add_user_superuser_failed(self):
        self.client.force_authenticate(user=self.superuser)
        add_response = self.client.post(self.url, self.add_user)
        self.assertEqual(add_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_user_unauthenticated(self):
        self.client.force_authenticate(user=self.regular_user)
        self.add_user["action"] = "add"
        add_response = self.client.post(self.url, self.add_user)
        self.assertEqual(add_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_user_success(self):
        self.client.force_authenticate(user=self.regular_user)
        user_account = dict(username="testuser", password="inipassword", action="remove")
        remove_response = self.client.post(self.url, user_account)
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
    
    def test_remove_user_wrong_username(self):
        self.client.force_authenticate(user=self.regular_user)
        user_account = dict(username="wronguser", password="inipassword", action="remove")
        remove_response = self.client.post(self.url, user_account)
        self.assertEqual(remove_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(remove_response.data['detail'], "username incompatible")

    def test_remove_user_wrong_password(self):
        self.client.force_authenticate(user=self.regular_user)
        user_account = dict(username="testuser", password="wrongpassword", action="remove")
        remove_response = self.client.post(self.url, user_account)
        self.assertEqual(remove_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(remove_response.data['detail'], "password incorrect")