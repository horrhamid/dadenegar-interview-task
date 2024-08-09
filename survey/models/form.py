from core import models


class Form(models.AuditableModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "DR", "پیش نویس"
        PUBLISHED = "PU", "منتشر شده"
        ARCHIVED = "AR", "بایگانی شده"
        DELETED = "DE", "حذف شده"

    class AvailabilityChoices(models.TextChoices):
        OPEN = "OP", ""
        CLOSE = "CL", ""
        RESTRICTED = "RS", ""

    title = models.CharField(max_length=250)
    description = models.TextField(null=True, default=None)
    subject = models.CharField(max_length=250, default="General")
    status = models.CharField(max_length=2, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    availability = models.CharField(max_length=2, choices=AvailabilityChoices.choices, default=AvailabilityChoices.OPEN)
    published_at = models.DateTimeField(null=True, blank=True, default=None)
    archived_at = models.DateTimeField(null=True, blank=True, default=None)
    owner = models.ForeignKey(
        to="Authentication.User",
        on_delete=models.SET_NULL,
        related_name="forms",
        related_query_name="form",
        null=True,
        default=None
    )

    def publish(self):
        self.status = self.StatusChoices.PUBLISHED
        self.published_at = models.now()
        self.save()

    def archive(self):
        self.status = self.StatusChoices.ARCHIVED
        self.archived_at = models.now()
        self.save()

