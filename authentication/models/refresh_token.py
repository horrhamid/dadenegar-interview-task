from core import models
from .. import constants


def default_refresh_token():
    return models.random_string(length=constants.REFRESH_TOKEN_LENGTH)


class AccessTokenManager(models.Manager):
    pass


class RefreshToken(models.CreatableModel, models.DeletableModel):
    user = models.ForeignKey(to="User", on_delete=models.CASCADE)
    token = models.CharField(
        max_length=constants.REFRESH_TOKEN_LENGTH,
        unique=True,
        db_index=True,
        default=default_refresh_token,
    )
