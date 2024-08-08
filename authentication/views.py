from rest_framework.permissions import AllowAny, IsAuthenticated
from . import models, serializers, messages, tasks
from rest_framework.decorators import action
from core import views, responses, permissions
from .actions import Actions
from django.utils import timezone


class AuthenticateView(views.BaseViewSet):
    permission_classes = [AllowAny]
    request_serializer = {
        "login": serializers.LoginSerializer,
        "refresh_token": serializers.RefreshTokenSerializer,
    }
    response_serializer = {
        "login": serializers.AccessTokenSerializer,
        "refresh_token": serializers.AccessTokenSerializer,
    }

    @action(methods=["POST"], detail=False)
    def login(self, request):
        try:
            serializer = self.get_request_serializer()(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = serializer.instance
            token = tasks.create_token(user_id=user.id)
            response_serializer = self.get_response_serializer()(token)

            return responses.Ok(
                response_serializer.data, message=messages.login_success_message
            )

        except models.User.DoesNotExist:
            return responses.UnAuthorized(
                message=messages.invalid_login_credentials_message
            )

    @action(methods=["POST"], detail=False)
    def refresh_token(self, request):
        try:
            serializer = self.get_request_serializer()(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            refresh_token = serializer.instance
            token = tasks.create_token(user_id=refresh_token.user.id)
            response_serializer = self.get_response_serializer()(token)
            return responses.Ok(response_serializer.data)

        except models.RefreshToken.DoesNotExist:
            return responses.NotAcceptable(
                message=messages.invalid_refresh_token_message
            )


class LogoutView(views.BaseViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        try:
            user = self.request.user
            models.AccessToken.objects.filter(user=user).update(
                deleted_at=timezone.now()
            )
            models.RefreshToken.objects.filter(user=user).update(
                deleted_at=timezone.now()
            )
            return responses.Ok(message=messages.logged_out_message)

        except models.RefreshToken.DoesNotExist:
            return responses.UnAuthorized(
                message=messages.invalid_refresh_token_message
            )


class SecretCredentialsView(views.ListModelMixin):
    permission_classes = [AllowAny]
    request_serializer = serializers.SecretCredentialRequestSerializer
    response_serializer = serializers.SecretCredentialSerializer

    @action(detail=True, methods=["POST"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_base_queryset(self):
        RequestSerializer = self.get_request_serializer()
        request_serializer = RequestSerializer(data=self.request.data)
        request_serializer.is_valid(raise_exception=True)
        request_serializer.save()
        user = request_serializer.instance
        return models.Credential.objects.filter(user=user)


class OTPView(views.BaseViewSet):
    permission_classes = [AllowAny]
    request_serializer = {
        "send_code": serializers.OTPSendSerializer,
        "reset_password": serializers.OTPResetPasswordSerializer,
    }
    response_serializer = {"reset_password": serializers.AccessTokenSerializer}

    @action(methods=["POST"], detail=False)
    def send_code(self, request):
        try:
            serializer = self.get_request_serializer()(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            credential = serializer.instance
            otp = models.OTP.objects.get_for_credential(credential=credential)
            if not otp.can_send():
                return responses.TooManyRequests(message=messages.otp_cant_send_message)
            otp.send_code()
            return responses.Ok(message=messages.otp_send_message)
        except models.User.DoesNotExist:
            return responses.NotFound(message=messages.otp_no_such_user_message)
        except responses.BadRequest as response:
            return response

    @action(methods=["POST"], detail=False)
    def reset_password(self, request):
        try:
            serializer = self.get_request_serializer()(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            credential = serializer.instance
            code = serializer.validated_data.get("code")
            password = serializer.validated_data.get("password")
            otp = models.OTP.objects.get_for_credential(credential=credential)
            if not otp.can_try():
                return responses.TooManyRequests(message=messages.otp_cant_try_message)
            valid_code = otp.try_code(code)
            if not valid_code:
                return responses.NotAcceptable(message=messages.otp_wrong_message)
            credential.user.set_password(password)
            credential.user.save()
            token = tasks.create_token(user_id=credential.user.id)
            response_serializer = self.get_response_serializer()(token)
            return responses.Ok(
                data=response_serializer.data, message=messages.otp_success_message
            )
        except models.User.DoesNotExist:
            return responses.NotFound(message=messages.otp_no_such_user_message)
        except responses.BadRequest as response:
            return response


class ConfigsView(views.RetrieveModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    response_serializer = serializers.ConfigsSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class UsersView(
    views.PaginateModelMixin,
    views.CreateModelMixin,
    views.DeleteModelMixin,
    views.EditModelMixin,
    views.RetrieveModelMixin,
    views.BaseViewSet,
):
    permission_classes = [permissions.CRUDActionPermission(Actions.users)]
    request_serializer = {
        "create": serializers.UserCreateUpdateSerializer,
        "edit": serializers.UserCreateUpdateSerializer,
    }
    response_serializer = {
        "paginate": serializers.UserRetrieveSerializer,
        "export_to_excel": serializers.UserRetrieveSerializer,
        "retrieve": serializers.UserRetrieveSerializer,
    }
    base_queryset = models.User.objects.all()
    ordering_choices = {
        "newest": "-date_joined",
        "oldest": "date_joined",
    }
    filter_lookups = {"groups": "groups__in"}


class GroupsView(
    views.CreateModelMixin,
    views.EditModelMixin,
    views.RetrieveModelMixin,
    views.ListModelMixin,
    views.DeleteModelMixin,
    views.PaginateModelMixin
):
    permission_classes = [permissions.CRUDActionPermission(Actions.groups)]
    response_serializer = {
        "list": serializers.GroupListSerializer,
        "export_to_excel": serializers.GroupListSerializer,
        "retrieve": serializers.GroupRetrieveSerializer,
    }

    request_serializer = {
        "create": serializers.GroupCreateUpdateSerializer,
        "edit": serializers.GroupCreateUpdateSerializer,
    }
    base_queryset = {
        "list": models.Group.objects.all(),
        "export_to_excel": models.Group.objects.all(),
        "retrieve": models.Group.objects.all(),
        "edit": models.Group.objects.all(),
        "delete": models.Group.objects.filter(key__isnull=True),
    }


class GroupUsersView(views.PaginateModelMixin):
    permission_classes = [permissions.CRUDActionPermission(Actions.groups)]
    response_serializer = serializers.BaseUserSerializer

    def get_base_queryset(self):
        return models.User.objects.filter(
            membership__group_id=self.kwargs.get("pk", None)
        )


class ActionsView(
    views.ListModelMixin,
    views.CreateModelMixin,
    views.DeleteModelMixin,
):
    permission_classes = [permissions.CRUDActionPermission("authentication.action")]
    base_queryset = {
        "list": models.Action.roots.all(),
        "delete": models.Action.objects.all(),
    }

    serializer_class = {
        "create": serializers.ActionCreateSerializer,
        "list": serializers.ActionRetrieveSerializer,
    }

    queryset = {
        "list": models.Action.roots.all(),
        "delete": models.Action.objects.all(),
    }


class TestView(views.EditModelMixin):
    permission_classes = [AllowAny]
    request_serializer = serializers.TestUserSerializer

    def get_object(self, *args, **kwargs):
        return models.User.objects.get(username="admin")


class LogsView(views.PaginateModelMixin):
    permission_classes = [permissions.ActionPermission(Actions.logs_view)]
    base_queryset = models.Log.objects.all()
    response_serializer = {
        "paginate": serializers.LogSerializer,
        "export_to_excel": serializers.ExportLogSerializer,
    }
    filter_lookups = {
        "from_date": "created_at__date__gte",
        "to_date": "created_at__date__lte",
        "user": "user__username",
        "action": "action__title",
    }
    search_lookups = ["user__first_name", "user__last_name", "action__title"]
    allow_page_size = True
    default_page_size = 50
