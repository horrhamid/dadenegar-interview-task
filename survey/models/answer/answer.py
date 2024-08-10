from core import models


class Answer(models.AuditableModel):

    class AnswerTypeChoices(models.TextChoices):
        TEXT = "TE", "تشریحی"
        RATING = "RA", "نظرسنجی"
        MULTIPLE_CHOICES = "MC", "چند گزینه ای"
        MATRIX = "MX", "ماتریسی"

    response = models.ForeignKey(
        to="survey.Response",
        on_delete=models.CASCADE,
        related_name="answers",
        related_query_name="answer",
        null=True,
        default=None
    )
    question = models.ForeignKey(
        to="survey.Question",
        on_delete=models.CASCADE,
        related_name="answers",
        related_query_name="answer"
    )
    type = models.CharField(max_length=20, choices=AnswerTypeChoices.choices, default=AnswerTypeChoices.TEXT)

    @property
    def creator(self):
        return self.response.creator

    def is_valid(self):
        raise NotImplementedError("This method should be implemented in subclasses.")
