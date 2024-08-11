from core import views, responses, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from . import serializers, models


class FormView(
    views.PaginateModelMixin,
    views.CreateModelMixin
):
    permission_classes = [IsAuthenticated]
    base_queryset = models.Form.alives.filter(archived_at=None)
    response_serializer = {
        "paginate": serializers.FormSerializer,
    }
    request_serializer = {
        "create": serializers.FormSerializer
    }

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(owner=self.request.user)
        return context


class QuestionView(
    views.PaginateModelMixin,
    views.CreateModelMixin
):
    permission_classes = [AllowAny]
    base_queryset = models.Question.objects.all()
    response_serializer = serializers.QuestionSerializer
    request_serializer = serializers.QuestionCreateSerializer


class AnswerView(
    views.PaginateModelMixin,
    views.CreateModelMixin
):
    permission_classes = [AllowAny]
    response_serializer = serializers.AnswerSerializer
    request_serializer = serializers.AnswerSerializer
    base_queryset = models.Answer.objects.all()


class ResponseView(
    views.PaginateModelMixin,
    views.CreateModelMixin
):
    permission_classes = [AllowAny]
    base_queryset = models.Response.alives.all()
    response_serializer = serializers.ResponseSerializer
    request_serializer = serializers.ResponseSerializer

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(owner=self.request.user)
        ip = self.get_client_ip()
        context.update(ip_address=ip)
        return context
