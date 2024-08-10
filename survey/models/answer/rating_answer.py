from .answer import Answer, models


class RatingAnswer(Answer):
    answer_value = models.IntegerField()

    def is_valid(self):
        return self.question.validate_answer(self.answer_value)
