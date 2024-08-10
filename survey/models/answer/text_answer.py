from .answer import Answer, models


class TextAnswer(Answer):
    answer_value = models.TextField()

    def is_valid(self):
        return self.question.validate_answer(self.answer_value)
