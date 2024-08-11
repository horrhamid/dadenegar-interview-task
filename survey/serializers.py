from core import serializers
from . import models


class QuestionSerializer(serializers.ModelSerializer):
    min_rating = serializers.SerializerMethodField()
    max_rating = serializers.SerializerMethodField()
    allow_multiple = serializers.SerializerMethodField()
    rows = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()

    class Meta:
        model = models.Question
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'form', 'min_rating', 'max_rating',
                  'allow_multiple', 'rows', 'columns', 'choices']

    def get_min_rating(self, obj):
        if obj.type == "RA":
            return models.RatingQuestion.objects.get(id=obj.id).min_rating
        else:
            return None

    def get_max_rating(self, obj):
        if obj.type == "RA":
            return models.RatingQuestion.objects.get(id=obj.id).max_rating
        else:
            return None

    def get_allow_multiple(self, obj):
        if obj.type == "MC":
            return models.MultipleChoiceQuestion.objects.get(id=obj.id).allow_multiple
        else:
            return None

    def get_choices(self, obj):
        if obj.type == "MC":
            return models.MultipleChoiceQuestion.objects.get(id=obj.id).choices
        else:
            return None

    def get_rows(self, obj):
        if obj.type == "MX":
            return models.MatrixQuestion.objects.get(id=obj.id).rows
        else:
            return None

    def get_columns(self, obj):
        if obj.type == "MX":
            return models.MatrixQuestion.objects.get(id=obj.id).columns
        else:
            return None


class RatingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RatingQuestion
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'form', 'min_rating', 'max_rating']


class TextQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TextQuestion
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'form']


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MultipleChoiceQuestion
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'form', 'allow_multiple', 'choices']


class MatrixQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MatrixQuestion
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'form', 'rows', 'columns']


class QuestionCreateSerializer(serializers.ModelSerializer):
    min_rating = serializers.IntegerField(required=False, allow_null=True)
    max_rating = serializers.IntegerField(required=False, allow_null=True)
    allow_multiple = serializers.BooleanField(required=False, allow_null=True)
    rows = serializers.JSONField(required=False, allow_null=True)
    columns = serializers.JSONField(required=False, allow_null=True)
    choices = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = models.Question
        fields = ['title', 'description', 'type', 'is_required', 'order', 'form', 'min_rating', 'max_rating',
                  'allow_multiple', 'choices', 'rows', 'columns']

    def create(self, validated_data):
        question_type = validated_data.get('type')
        if question_type == models.Question.QuestionTypeChoices.RATING:
            if "rows" in validated_data:
                validated_data.pop("rows")
            if "columns" in validated_data:
                validated_data.pop("columns")
            if "allow_multiple" in validated_data:
                validated_data.pop("allow_multiple")
            if "choices" in validated_data:
                validated_data.pop("choices")
            return models.RatingQuestion.objects.create(**validated_data)
        elif question_type == models.Question.QuestionTypeChoices.TEXT:
            if "min_rating" in validated_data:
                validated_data.pop("min_rating")
            if "max_rating" in validated_data:
                validated_data.pop("max_rating")
            if "rows" in validated_data:
                validated_data.pop("rows")
            if "columns" in validated_data:
                validated_data.pop("columns")
            if "allow_multiple" in validated_data:
                validated_data.pop("allow_multiple")
            if "choices" in validated_data:
                validated_data.pop("choices")
            return models.TextQuestion.objects.create(**validated_data)
        elif question_type == models.Question.QuestionTypeChoices.MULTIPLE_CHOICES:
            if "min_rating" in validated_data:
                validated_data.pop("min_rating")
            if "max_rating" in validated_data:
                validated_data.pop("max_rating")
            if "rows" in validated_data:
                validated_data.pop("rows")
            if "columns" in validated_data:
                validated_data.pop("columns")
            return models.MultipleChoiceQuestion.objects.create(**validated_data)
        elif question_type == models.Question.QuestionTypeChoices.MATRIX:
            if "min_rating" in validated_data:
                validated_data.pop("min_rating")
            if "max_rating" in validated_data:
                validated_data.pop("max_rating")
            if "allow_multiple" in validated_data:
                validated_data.pop("allow_multiple")
            if "choices" in validated_data:
                validated_data.pop("choices")
            return models.MatrixQuestion.objects.create(**validated_data)
        else:
            return models.Question.objects.create(**validated_data)


class QuestionFormSerializer(QuestionCreateSerializer):
    class Meta(QuestionCreateSerializer):
        model = models.Question
        fields = ['id', 'title', 'description', 'type', 'is_required', 'order', 'min_rating', 'max_rating',
                  'allow_multiple', 'choices', 'rows', 'columns']


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionFormSerializer(many=True)

    class Meta:
        model = models.Form
        fields = ['id', 'title', 'description', 'subject', 'status', 'availability', 'questions']

    def create(self, validated_data):
        owner = self.context.get("owner", None)
        validated_data["owner"] = owner
        questions_data = validated_data.pop('questions')
        if validated_data.get("status") == "PU":
            validated_data["published_at"] = models.models.now()
        form = models.Form.objects.create(**validated_data)
        for question_data in questions_data:
            question_type = question_data.get('type')
            question_data["form"] = form
            if question_type == models.Question.QuestionTypeChoices.RATING:
                if "rows" in question_data:
                    question_data.pop("rows")
                if "columns" in question_data:
                    question_data.pop("columns")
                if "allow_multiple" in question_data:
                    question_data.pop("allow_multiple")
                if "choices" in question_data:
                    question_data.pop("choices")
                return models.RatingQuestion.objects.create(**question_data)
            elif question_type == models.Question.QuestionTypeChoices.TEXT:
                if "min_rating" in question_data:
                    question_data.pop("min_rating")
                if "max_rating" in question_data:
                    question_data.pop("max_rating")
                if "rows" in question_data:
                    question_data.pop("rows")
                if "columns" in question_data:
                    question_data.pop("columns")
                if "allow_multiple" in question_data:
                    question_data.pop("allow_multiple")
                if "choices" in question_data:
                    question_data.pop("choices")
                return models.TextQuestion.objects.create(**question_data)
            elif question_type == models.Question.QuestionTypeChoices.MULTIPLE_CHOICES:
                if "min_rating" in question_data:
                    question_data.pop("min_rating")
                if "max_rating" in question_data:
                    question_data.pop("max_rating")
                if "rows" in question_data:
                    question_data.pop("rows")
                if "columns" in question_data:
                    question_data.pop("columns")
                return models.MultipleChoiceQuestion.objects.create(**question_data)
            elif question_type == models.Question.QuestionTypeChoices.MATRIX:
                if "min_rating" in question_data:
                    question_data.pop("min_rating")
                if "max_rating" in question_data:
                    question_data.pop("max_rating")
                if "allow_multiple" in question_data:
                    question_data.pop("allow_multiple")
                if "choices" in question_data:
                    question_data.pop("choices")
                return models.MatrixQuestion.objects.create(**question_data)
            else:
                return models.Question.objects.create(**question_data)
        return form


class MatrixAnswerSerializer(serializers.ModelSerializer):
    answer_value = serializers.JSONField()

    class Meta:
        model = models.MatrixAnswer
        fields = ['id', 'response', 'question', 'type', 'answer_value']


class MultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    answer_value = serializers.JSONField()

    class Meta:
        model = models.MultipleChoiceAnswer
        fields = ['id', 'response', 'question', 'type', 'answer_value']


class RatingAnswerSerializer(serializers.ModelSerializer):
    answer_value = serializers.IntegerField()

    class Meta:
        model = models.RatingAnswer
        fields = ['id', 'response', 'question', 'type', 'answer_value']


class TextAnswerSerializer(serializers.ModelSerializer):
    answer_value = serializers.CharField()

    class Meta:
        model = models.TextAnswer
        fields = ['id', 'response', 'question', 'type', 'answer_value']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TextAnswer
        fields = ['id', 'response', 'question', 'type', 'answer_value']

    def get_subclass_instance(self, instance):
        if instance.type == models.Answer.AnswerTypeChoices.TEXT:
            return models.TextAnswer.objects.get(id=instance.id)
        elif instance.type == models.Answer.AnswerTypeChoices.RATING:
            return models.RatingAnswer.objects.get(id=instance.id)
        elif instance.type == models.Answer.AnswerTypeChoices.MULTIPLE_CHOICES:
            return models.MultipleChoiceAnswer.objects.get(id=instance.id)
        elif instance.type == models.Answer.AnswerTypeChoices.MATRIX:
            return models.MatrixAnswer.objects.get(id=instance.id)
        else:
            raise serializers.ValidationError(f"Invalid answer type: {instance.type}")

    def get_serializer_for_instance(self, instance):
        subclass_instance = self.get_subclass_instance(instance)
        if isinstance(subclass_instance, models.TextAnswer):
            if not isinstance(subclass_instance.answer_value, str):
                raise ValueError("The answer value most be string")
            return TextAnswerSerializer(subclass_instance)
        elif isinstance(subclass_instance, models.RatingAnswer):
            if not isinstance(subclass_instance.answer_value, int):
                raise ValueError("The answer value most be number")
            return RatingAnswerSerializer(subclass_instance)
        elif isinstance(subclass_instance, models.MultipleChoiceAnswer):
            if not isinstance(subclass_instance.answer_value, str) and not isinstance(subclass_instance.answer_value,
                                                                                      list):
                raise ValueError("The answer value most be string or list")
            return MultipleChoiceAnswerSerializer(subclass_instance)
        elif isinstance(subclass_instance, models.MatrixAnswer):
            if not isinstance(subclass_instance.answer_value, dict):
                raise ValueError("The answer value most be dict")
            return MatrixAnswerSerializer(subclass_instance)
        else:
            raise serializers.ValidationError(f"Invalid answer type: {instance.type}")

    def to_representation(self, instance):
        serializer = self.get_serializer_for_instance(instance)
        return serializer.data

    def to_internal_value(self, data):
        answer_type = data.get('type')
        if answer_type == models.Answer.AnswerTypeChoices.TEXT:
            serializer = TextAnswerSerializer(data=data)
        elif answer_type == models.Answer.AnswerTypeChoices.RATING:
            serializer = RatingAnswerSerializer(data=data)
        elif answer_type == models.Answer.AnswerTypeChoices.MULTIPLE_CHOICES:
            serializer = MultipleChoiceAnswerSerializer(data=data)
        elif answer_type == models.Answer.AnswerTypeChoices.MATRIX:
            serializer = MatrixAnswerSerializer(data=data)
        else:
            raise serializers.ValidationError("Invalid answer type.")

        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def create(self, validated_data):
        answer_type = validated_data['type']
        if answer_type == models.Answer.AnswerTypeChoices.TEXT:
            return models.TextAnswer.objects.create(**validated_data)
        elif answer_type == models.Answer.AnswerTypeChoices.RATING:
            return models.RatingAnswer.objects.create(**validated_data)
        elif answer_type == models.Answer.AnswerTypeChoices.MULTIPLE_CHOICES:
            return models.MultipleChoiceAnswer.objects.create(**validated_data)
        elif answer_type == models.Answer.AnswerTypeChoices.MATRIX:
            return models.MatrixAnswer.objects.create(**validated_data)
        else:
            raise serializers.ValidationError("Invalid answer type provided.")


class ResponseAnswerSerializer(AnswerSerializer):
    class Meta(AnswerSerializer.Meta):
        model = models.TextAnswer
        fields = ['id', 'question', 'type', 'answer_value']


class ResponseSerializer(serializers.ModelSerializer):
    answers = ResponseAnswerSerializer(many=True)

    class Meta:
        model = models.Response
        fields = ['id', 'status', 'form', 'answers', 'created_at', 'updated_at']

    def create(self, validated_data):
        creator = self.context.get("creator", None)
        validated_data["creator"] = creator
        ip_address = self.context.get("ip_address", None)
        validated_data["ip_address"] = ip_address
        answers_data = validated_data.pop('answers')
        response = models.Response.objects.create(**validated_data)

        for answer_data in answers_data:
            question = answer_data['question']
            answer_type = answer_data['type']

            if answer_type == models.Answer.AnswerTypeChoices.TEXT:
                models.TextAnswer.objects.create(response=response, question_id=question.id, **answer_data)
            elif answer_type == models.Answer.AnswerTypeChoices.RATING:
                models.RatingAnswer.objects.create(response=response, question_id=question.id, **answer_data)
            elif answer_type == models.Answer.AnswerTypeChoices.MULTIPLE_CHOICES:
                models.MultipleChoiceAnswer.objects.create(response=response, question_id=question.id, **answer_data)
            elif answer_type == models.Answer.AnswerTypeChoices.MATRIX:
                models.MatrixAnswer.objects.create(response=response, question_id=question.id, **answer_data)
            else:
                raise serializers.ValidationError("Invalid answer type.")

        return response
