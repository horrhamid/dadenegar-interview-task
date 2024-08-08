from core import models


class Membership(models.CreatableModel):
    user = models.ForeignKey(
        to="User",
        on_delete=models.CASCADE,
        related_name="memberships",
        related_query_name="membership",
    )
    group = models.ForeignKey(
        to="Group",
        on_delete=models.CASCADE,
        related_name="memberships",
        related_query_name="membership",
    )
