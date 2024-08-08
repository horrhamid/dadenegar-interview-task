from django.urls import re_path
from .. import views

app_name = "authentication_private"
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
        views.SecretCredentialsView.as_list(),
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
        views.ConfigsView.as_retrieve(),
    ),
    re_path(
        r"^users/$",
        views.UsersView.as_create_paginate(),
    ),
    re_path(
        r"^users/export-to-excel/$",
        views.UsersView.as_export_to_excel(),
    ),
    re_path(
        r"^users/(?P<pk>[0-9]+)/$",
        views.UsersView.as_edit_delete_retrieve(),
    ),
    re_path(
        r"^users/(?P<user_pk>[0-9]+)/credentials/$",
        views.UsersView.as_view(
            actions={
                "delete": "delete",
                "get": "retrieve",
                "post": "edit",
            }
        ),
    ),
    re_path(
        r"^groups/$",
        views.GroupsView.as_create_list(),
    ),
    re_path(
        r"^groups/export-to-excel/$",
        views.GroupsView.as_export_to_excel(),
    ),
    re_path(
        r"^groups/(?P<pk>[0-9]+)/$",
        views.GroupsView.as_edit_delete_retrieve(),
    ),
    re_path(
        r"^groups/(?P<pk>[0-9]+)/users/$",
        views.GroupUsersView.as_paginate(),
    ),
    re_path(
        r"^logs/$",
        views.LogsView.as_paginate(),
    ),
    re_path(
        r"^logs/export-to-excel/$",
        views.LogsView.as_export_to_excel(),
    ),
]
