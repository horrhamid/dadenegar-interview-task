from core import models


class Question(models.AuditableModel):
    class QuestionTypeChoices(models.TextChoices):
        TEXT = "TE", "تشریحی"
        RATING = "RA", "نظرسنجی"
        MULTIPLE_CHOICES = "MC", "چند گزینه ای"
        MATRIX = "MX", "ماتریسی"

    title = models.CharField(max_length=250, null=True, default=None)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=QuestionTypeChoices.choices, default=QuestionTypeChoices.TEXT)
    is_required = models.BooleanField(default=False)
    order = models.IntegerField()
    form = models.ForeignKey(
        to="survey.Form",
        on_delete=models.CASCADE,
        related_name="questions",
        related_query_name="question",
        null=True,
        default=None
    )

    @property
    def creator(self):
        return self.form.owner

    def get_question_type(self):
        return self.type

    def validate_answer(self, answer):
        raise NotImplementedError("This method should be implemented in subclasses.")
