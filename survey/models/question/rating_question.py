from .question import Question, models


class RatingQuestion(Question):
    min_rating = models.IntegerField(default=1)
    max_rating = models.IntegerField(default=5)

    def validate_answer(self, answer):
        return isinstance(answer, int) and self.min_rating <= answer <= self.max_rating
