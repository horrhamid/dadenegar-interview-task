from core import models


class Group(models.Model):
    title = models.CharField(max_length=50)
    key = models.CharField(
        max_length=20, null=True, blank=True, default=None, unique=True
    )

    @property
    def user_count(self):
        return self.users.count()

    def __str__(self) -> str:
        return self.title

    @property
    def is_deletable(self):
        return self.key is None

    @property
    def actions(self):
        from .action import Action

        return Action.objects.filter(grant__group=self)
