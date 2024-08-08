from django.urls import re_path
from .. import views

app_name = "public_authentication"
urlpatterns = [
    re_path(
        r"^login/$",
        views.AuthenticateView.as_view(actions={"post": "login"}),
    ),
    re_path(
        r"^refresh-token/$",
        views.AuthenticateView.as_view(actions={"post": "refresh_token"}),
    ),
    re_path(
        r"^logout/$",
        views.LogoutView.as_view(actions={"post": "logout"}),
    ),
    re_path(
        r"^users/credentials/$",
        views.SecretCredentialsView.as_view(actions={"post": "list"}),
    ),
    re_path(
        r"^otp/send-code/$",
        views.OTPView.as_view(actions={"post": "send_code"}),
    ),
    re_path(
        r"^otp/reset-password/$",
        views.OTPView.as_view(actions={"post": "reset_password"}),
    ),
    re_path(
        r"^configs/",
        views.ConfigsView.as_view(actions={"get": "retrieve"}),
    ),
]
