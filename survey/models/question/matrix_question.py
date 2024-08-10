from .question import Question, models


class MatrixQuestion(Question):
    rows = models.JSONField(default=list)
    columns = models.JSONField(default=list)

    def validate_answer(self, answer):
        if isinstance(answer, dict):
            for row, column in answer.items():
                if row not in self.rows or column not in self.columns:
                    return False
            return True
        return False

    def save(self, *args, **kwargs):
        self.question_type = 'matrix'
        super().save(*args, **kwargs)
