from . import models
from django.utils import timezone


def fill_path(path_regex: str, kwargs):
    if not path_regex or len(path_regex) == 0:
        return ""
    regex_parts = path_regex.split(".")
    filled_parts = []
    for part in regex_parts:
        if part.startswith("<") and part.endswith(">"):
            key = part[1:-1]
            filled_part = kwargs.get(key)
        else:
            filled_part = part
        filled_parts.append(filled_part)
    return ".".join(filled_parts)


def check_access(user, path_regex: str, kwargs):
    from authentication.models import Grant, Action, Log, User

    path = fill_path(path_regex, kwargs)
    try:
        action = Action.objects.get(path=path)
        paths = []
        super_action = action
        while super_action is not None:
            paths.append(super_action.path)
            super_action = super_action.parent

        has_group_access = Grant.objects.filter(
            group__membership__user=user,
            action__path__in=paths,
        ).exists()
        has_user_access = user.actions.filter(path__in=paths).exists()
        has_super_access = user.is_superuser
        has_access = has_group_access or has_user_access or has_super_access
        if action.is_loggable:
            Log.objects.create(user=user, action=action, granted=has_access)
        return has_access
    except Action.DoesNotExist:
        return True


def grant_access(group_id: int, path: str):
    from .models import Grant, Action

    return Grant.objects.create(
        group_id=group_id, action_id=Action.objects.get(path=path).id
    )


def verify_token(token: str):
    from .models import AccessToken
    from django.utils import timezone

    try:
        access_token = (
            AccessToken.objects.filter(
                deleted_at=None, token=token, expire_at__gt=timezone.now()
            )
            .only("user_id")
            .first()
        ).user_id
        return access_token.user_id
    except AccessToken.DoesNotExist:
        return None


def create_token(user_id):
    from django.conf import settings

    if not settings.ENV.IS_LOCAL:
        models.AccessToken.objects.filter(user_id=user_id).update(
            deleted_at=timezone.now()
        )
        models.RefreshToken.objects.filter(user_id=user_id).update(
            deleted_at=timezone.now()
        )
    refresh_token = models.RefreshToken.objects.create(user_id=user_id)
    access_token = models.AccessToken.objects.create(
        user_id=user_id, refresh=refresh_token
    )
    return access_token
