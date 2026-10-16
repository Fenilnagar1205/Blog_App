from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationTests(APITestCase):
    url = "/accounts/register/"

    def test_user_registration_success(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPass123!xyz",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("StrongPass123!xyz"))

    def test_duplicate_username_rejected(self):
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="StrongPass123!xyz",
        )

        data = {
            "username": "existinguser",
            "email": "another@example.com",
            "password": "StrongPass456!xyz",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected_case_insensitive(self):
        User.objects.create_user(
            username="firstuser",
            email="existing@example.com",
            password="StrongPass123!xyz",
        )

        data = {
            "username": "seconduser",
            "email": "EXISTING@example.com",
            "password": "StrongPass456!xyz",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_rejected(self):
        data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_not_returned_in_response(self):
        data = {
            "username": "responseuser",
            "email": "response@example.com",
            "password": "StrongPass123!xyz",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)


class AccountAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="accountuser",
            email="account@example.com",
            password="StrongPass123!xyz",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="OtherPass123!xyz",
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_current_user_endpoint(self):
        response = self.client.get("/accounts/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "accountuser")
        self.assertEqual(response.data["email"], "account@example.com")

    def test_current_user_requires_authentication(self):
        self.client.credentials()

        response = self.client.get("/accounts/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_success(self):
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }

        response = self.client.patch("/accounts/profile/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_profile_update_rejects_other_users_email(self):
        response = self.client.patch(
            "/accounts/profile/",
            {"email": self.other_user.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_success(self):
        response = self.client.post(
            "/accounts/change-password/",
            {
                "old_password": "StrongPass123!xyz",
                "new_password": "NewStrongPass456!xyz",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456!xyz"))

    def test_password_change_rejects_wrong_old_password(self):
        response = self.client.post(
            "/accounts/change-password/",
            {
                "old_password": "WrongPassword123!",
                "new_password": "NewStrongPass456!xyz",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklists_refresh_token(self):
        response = self.client.post(
            "/accounts/logout/",
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
