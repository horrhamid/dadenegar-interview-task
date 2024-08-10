from .answer import Answer, models


class MultipleChoiceAnswer(Answer):
    answer_value = models.JSONField()

    def is_valid(self):
        return self.question.validate_answer(self.answer_value)
