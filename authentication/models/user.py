import string
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from core import models, validators
from .. import messages


def default_username():
    return models.random_string(32, string.ascii_lowercase)


class UserManager(DjangoUserManager, models.Manager):
    def get_by_credentials(self, username, password):
        user = self.get_by_username(username)

        valid_password = user.check_password(password)
        if not valid_password:
            raise User.DoesNotExist()
        return user

    def get_by_username(self, username):
        return self.get(username=username)


class User(AbstractUser):
    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    REQUIRED_FIELDS = []
    is_blocked = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        "Group",
        blank=True,
        related_name="users",
        related_query_name="user",
        through="Membership",
    )
    actions = models.ManyToManyField(
        to="authentication.Action",
        blank=True,
        related_name="users",
        related_query_name="user",
    )

    def save(self, *args, **kwargs):
        in_create = self.pk is None
        in_bulk = False
        super().save(*args, **kwargs)
        self.post_save(in_create, in_bulk)

    is_admin = models.BooleanField(default=False)

    def grant_actions(self, actions):
        pass
        # self.actions.set(actions)
        # self.save()

    def block(self):
        from . import AccessToken, RefreshToken

        AccessToken.objects.filter(user=self).delete()
        RefreshToken.objects.filter(user=self).delete()
        self.is_blocked = True
        self.save()

    def __str__(self):
        return self.username

    def all_actions(self):
        from authentication.models import Action

        return self.actions.union(
            Action.objects.filter(grant__group__membership__user=self).distinct()
        )

    def set_groups(self, groups):
        from .membership import Membership

        current_memberships = self.memberships.all()
        for membership in current_memberships:
            if membership.group not in groups:
                membership.delete()

        create_memberships = []
        for group in groups:
            current_membership = None
            for membership in current_memberships:
                if membership.group == group:
                    current_membership = membership
            if not current_membership:
                create_memberships.append(Membership(group=group, user=self))
        Membership.objects.bulk_create(create_memberships)

    def post_save(self, in_create, in_bulk, index=None):
        from .action import Action

        if in_create:
            edit_action = Action(
                path=f"authentication.users.edit.{self.pk}",
                title=f"ویرایش {self.username}",
            )
            view_action = Action(
                path=f"authentication.users.view.{self.pk}",
                title=f"مشاهده اطلاعات {self.username}",
            )
            actions = [edit_action, view_action]

            actions = Action.register_actions(actions)
            self.grant_actions(actions)
