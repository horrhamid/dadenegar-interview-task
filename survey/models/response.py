from core import models


class Response(models.AuditableModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "DR", "پیش نویس"
        PUBLISHED = "PU", "منتشر شده"
        ARCHIVED = "AR", "بایگانی شده"
    ip_address = models.CharField(max_length=15, null=True, default=None)
    status = models.CharField(max_length=2, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    creator = models.ForeignKey(
        to="authentication.User",
        on_delete=models.SET_NULL,
        related_name="responses",
        related_query_name="response",
        null=True,
        default=None
    )
    form = models.ForeignKey(
        to="survey.Form",
        on_delete=models.CASCADE,
        related_name="responses",
        related_query_name="response"
    )