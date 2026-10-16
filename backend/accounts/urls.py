from django.urls import path
from .views import (
    UserRegistrationView,
    CurrentUserView,
    ProfileUpdateView,
    PasswordChangeView,
    LogoutView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register-user"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("profile/", ProfileUpdateView.as_view(), name="profile-update"),
    path("change-password/", PasswordChangeView.as_view(), name="change-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
