from core import models


class Log(models.CreatableModel):
    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey(
        to="authentication.User",
        related_name="logs",
        related_query_name="log",
        on_delete=models.CASCADE,
    )
    action = models.ForeignKey(
        to="Action",
        related_name="logs",
        related_query_name="log",
        on_delete=models.CASCADE,
    )
    granted = models.BooleanField(default=True)
