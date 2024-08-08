from core import models


class Grant(models.CreatableModel):
    action = models.ForeignKey(
        to="Action",
        related_name="grants",
        related_query_name="grant",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        to="Group",
        related_name="grants",
        related_query_name="grant",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.group} on {self.action}"

    @staticmethod
    def get_longest(grants):
        longest = None
        for grant in grants:
            if longest is None or len(grant.action.path) > len(longest.path):
                longest = grant.action
        return longest
