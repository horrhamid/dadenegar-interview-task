from .question import Question, models


class TextQuestion(Question):
    def validate_answer(self, answer):
        return isinstance(answer, str) and (not self.is_required or len(answer) > 0)
