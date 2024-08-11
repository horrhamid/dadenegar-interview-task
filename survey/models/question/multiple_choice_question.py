from .question import Question, models


class MultipleChoiceQuestion(Question):
    allow_multiple = models.BooleanField(default=False)
    choices = models.JSONField()

    def validate_answer(self, answer):
        if self.allow_multiple:
            return isinstance(answer, list) and all(isinstance(option, str) for option in answer)
        else:
            return isinstance(answer, str)

    def save(self, *args, **kwargs):
        self.question_type = 'multiple_choice'
        super().save(*args, **kwargs)
