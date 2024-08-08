from django.contrib import admin
from . import models
from django.contrib.auth.models import Group as DjangoGroup

# Register your models here.

admin.site.unregister(DjangoGroup)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "first_name",
        "last_name",
        "date_joined",
        "is_superuser",
        "is_active",
    ]


@admin.register(models.Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ["user", "id", "type", "credential"]
    raw_id_fields = ["user"]


@admin.register(models.OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = [
        "credential",
        "code",
        "send_count",
        "tried_count",
        "last_send",
        "last_tried",
    ]
    raw_id_fields = ["credential"]


@admin.register(models.AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "expire_at", "deleted_at"]
    raw_id_fields = ["user"]


@admin.register(models.RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token", "deleted_at"]
    raw_id_fields = ["user"]


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]


@admin.register(models.Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ["group", "action"]


@admin.register(models.Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ["title", "path", "parent", "is_visible"]


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ["action", "user", "created_at", "granted"]
    raw_id_fields = ["user"]


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["group", "user", "created_at"]
    raw_id_fields = ["user"]
