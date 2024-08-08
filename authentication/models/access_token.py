from .. import constants
from core import models


def default_access_token():
    return models.random_string(length=constants.ACCESS_TOKEN_LENGTH)


def default_access_token_expire():
    return models.future(seconds=constants.ACCESS_TOKEN_EXPIRE_TIME)


class AccessTokenManager(models.Manager):
    pass


class AccessToken(models.CreatableModel, models.DeletableModel):
    objects = AccessTokenManager()
    user = models.ForeignKey(to="User", on_delete=models.CASCADE)
    token = models.CharField(
        max_length=constants.ACCESS_TOKEN_LENGTH,
        unique=True,
        db_index=True,
        default=default_access_token,
    )
    refresh = models.OneToOneField(
        to="RefreshToken", on_delete=models.CASCADE, default=None
    )
    expire_at = models.DateTimeField(default=default_access_token_expire)

    @property
    def access_token(self):
        return self.token

    @property
    def refresh_token(self):
        return self.refresh.token
