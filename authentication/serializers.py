from core import responses, validators, serializers
from . import messages, models


class BaseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ["id", "title", "is_deletable"]


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "first_name", "last_name"]


class BaseActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Action
        fields = ["id", "title", "path"]


class AccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccessToken
        fields = ["access_token", "refresh_token", "expire_at"]


class CredentialRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Credential
        fields = ["id", "type", "credential"]


class CredentialCreateSerializer(serializers.NestedModelSerializer):
    class Meta:
        model = models.Credential
        fields = ["type", "credential"]

    type = serializers.ChoiceField(
        choices=[models.Credential.MOBILE, models.Credential.EMAIL]
    )
    credential = serializers.CharField()

    def validate(self, attrs):
        attr = super().validate(attrs)
        type = attr.get("type")
        credential = attr.get("credential")
        if type == models.Credential.MOBILE:
            validators.Mobile(credential)
        if type == models.Credential.EMAIL:
            validators.Email(credential)
        attr.update(user=self.context.get("user"))
        return attr


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "groups",
            "credentials",
        ]

    credentials = CredentialCreateSerializer(many=True, required=False)
    groups = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=models.Group.objects.all()),
        allow_null=True,
        required=False,
        default=[],
    )
    username = serializers.CharField(
        max_length=100,
        allow_null=True,
        allow_blank=True,
        default=None,
        required=False,
        validators=[
            validators.NotIn(
                models.User.objects.all(), "username", messages.duplicate_username_error
            )
        ],
    )
    password = serializers.CharField(
        max_length=100, allow_null=True, allow_blank=True, default=None, required=False
    )

    def get_nested_context(self, key) -> dict:
        return {"user": self.instance}

    def validate(self, attrs):
        password = attrs.get("password", None)
        username = attrs.get("username", None)
        if self.instance is None and password is None:
            raise validators.DjangoValidationError(
                {
                    "password": validators.ValidationError(
                        message=messages.password_is_required
                    )
                }
            )
        if self.instance is None and username is None:
            raise validators.DjangoValidationError(
                {
                    "username": validators.ValidationError(
                        message=messages.username_is_required
                    )
                }
            )
        if self.instance is not None and username is not None:
            if (
                models.User.objects.exclude(id=self.instance.id)
                .filter(username=username)
                .exists()
            ):
                raise validators.DjangoValidationError(
                    {
                        "username": validators.ValidationError(
                            message=messages.duplicate_username_error
                        )
                    }
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        print("inside updateee")

        password = validated_data.pop("password", None)
        username = validated_data.pop("username", None)
        groups = validated_data.pop("groups", [])
        if username:
            instance.username = username
        if password:
            instance.set_password(password)
        user = super().update(instance, validated_data)
        user.set_groups(groups)
        return user

    def create(self, validated_data):
        password = validated_data.pop("password")
        groups = validated_data.pop("groups", [])
        user = super().create(validated_data)
        user.is_active = True
        user.set_password(password)
        user.save()
        user.set_groups(groups)
        return user


class TestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "credentials"]

    credentials = CredentialCreateSerializer(many=True)

    def get_nested_context(self, key) -> dict:
        return {"user": self.instance}


class ConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_admin",
            "is_superuser",
            "first_name",
            "last_name",
            "all_actions",
            "latest_nav",
            "adjustment",
            "investor_count",
            "ordinary_unit_count",
            "special_unit_count",
            "total_instruments",
        ]

    all_actions = serializers.SerializerMethodField()
    latest_nav = serializers.SerializerMethodField()
    adjustment = serializers.SerializerMethodField()
    investor_count = serializers.SerializerMethodField()
    ordinary_unit_count = serializers.SerializerMethodField()
    special_unit_count = serializers.SerializerMethodField()
    total_instruments = serializers.SerializerMethodField()

    def get_all_actions(self, obj):
        actions_list = []
        for action in obj.all_actions():
            actions_list.append(action.path)
        return actions_list

    def get_latest_nav(self, obj):
        from orders.models import Nav
        from orders.serializers import NavListSerializer
        from accounting.models import Transaction, FiscalYear

        fiscal_year = FiscalYear.objects.get_default()
        if fiscal_year:
            latest_nav = (
                Nav.objects.filter(
                    models.models.Q(date__gte=fiscal_year.start)
                    & models.models.Q(date__lte=fiscal_year.end)
                )
                .order_by("date")
                .last()
            )
            if latest_nav:
                return NavListSerializer(latest_nav).data
            else:
                n = Nav()
                return NavListSerializer(n).data
        else:
            n = Nav()
            return NavListSerializer(n).data

    def get_adjustment(self, obj):
        from accounting.models import Transaction, FiscalYear

        fiscal_year = FiscalYear.objects.get_default()
        if fiscal_year:
            year_filter = models.models.Q(
                voucher__date__gte=fiscal_year.start
            ) & models.models.Q(voucher__date__lte=fiscal_year.end)
            code_1 = Transaction.balance(
                Transaction.alives.filter(
                    year_filter & models.models.Q(subsidiary__general__coding__code=1)
                )
            )
            code_2 = Transaction.balance(
                Transaction.alives.filter(
                    year_filter & models.models.Q(subsidiary__general__coding__code=2)
                )
            )
            code_3 = Transaction.balance(
                Transaction.alives.filter(
                    year_filter & models.models.Q(subsidiary__general__coding__code=3)
                )
            )
            code_4 = Transaction.balance(
                Transaction.alives.filter(
                    year_filter & models.models.Q(subsidiary__general__coding__code=4)
                )
            )
            code_5 = Transaction.balance(
                Transaction.alives.filter(
                    year_filter & models.models.Q(subsidiary__general__coding__code=5)
                )
            )
            return {
                "total_assets": code_1,
                "total_depths": code_2,
                "total_benefit_loss": code_3 + code_4 - code_5,
            }
        else:
            return {
                "total_assets": None,
                "total_depths": None,
                "total_benefit_loss": None,
            }

    def get_investor_count(self, obj):
        from investors.models import InvestorAccount

        return InvestorAccount.objects.count()

    def get_ordinary_unit_count(self, obj):
        from orders.models import OrderTransaction
        from accounting.models import StorageType, FiscalYear

        fiscal_year = FiscalYear.objects.get_default()
        if fiscal_year:
            year_filter = models.models.Q(
                voucher__date__gte=fiscal_year.start
            ) & models.models.Q(voucher__date__lte=fiscal_year.end)
            return (
                OrderTransaction.alives.filter(
                    year_filter
                    & models.models.Q(
                        storages__storage_type__key=StorageType.INVESTOR_ORDER_UNITS
                    )
                )
                .aggregate(sum_count=models.models.Sum("count"))
                .get("sum_count")
                or 0
            )

    def get_special_unit_count(self, obj):
        from orders.models import OrderTransaction
        from accounting.models import StorageType, FiscalYear

        fiscal_year = FiscalYear.objects.get_default()
        if fiscal_year:
            year_filter = models.models.Q(
                voucher__date__gte=fiscal_year.start
            ) & models.models.Q(voucher__date__lte=fiscal_year.end)
            return (
                OrderTransaction.alives.filter(
                    year_filter
                    & models.models.Q(
                        storages__storage_type__key=StorageType.INVESTOR_SPECIAL_ORDER_UNITS
                    )
                )
                .aggregate(sum_count=models.models.Sum("count"))
                .get("sum_count")
                or 0
            )

    def get_total_instruments(self, obj):
        from accounting.models import StorageType, FiscalYear, Transaction

        fiscal_year = FiscalYear.objects.get_default()
        if fiscal_year:
            year_filter = models.models.Q(
                voucher__date__gte=fiscal_year.start
            ) & models.models.Q(voucher__date__lte=fiscal_year.end)
            return (
                Transaction.alives.filter(
                    year_filter
                    & models.models.Q(
                        storages__storage_type__key__in=[
                            StorageType.INSTRUMENT_INVESTMENT,
                            StorageType.INSTRUMENT_EVALUATION,
                        ]
                    )
                )
                .aggregate(sum_amount=models.models.Sum("amount"))
                .get("sum_amount")
                or 0
            )


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "all_actions",
            "is_superuser",
            "groups",
            "credentials",
        ]

    all_actions = serializers.SerializerMethodField()
    groups = BaseGroupSerializer(many=True)
    credentials = CredentialRetrieveSerializer(many=True)

    def get_all_actions(self, obj):
        actions_list = []
        for action in obj.all_actions():
            actions_list.append(action.path)
        return actions_list


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "password"]

    username = serializers.CharField()
    password = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return models.User.objects.get_by_credentials(**validated_data)


class SecretCredentialRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

    def save(self):
        try:
            self.instance = models.User.objects.get_by_username(
                username=self.validated_data.get("username")
            )
        except models.User.DoesNotExist:
            raise responses.NotFound(message=messages.invalid_username_message)
        return self.instance


class SecretCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Credential
        fields = ["id", "type", "secret_credential"]


class OTPSendSerializer(serializers.Serializer):
    username = serializers.CharField()
    credential = serializers.IntegerField()

    def save(self):
        try:
            user = models.User.objects.get_by_username(
                username=self.validated_data.get("username")
            )
            credential = models.Credential.objects.get(
                id=self.validated_data.get("credential")
            )
            if credential.user != user:
                raise responses.NotAcceptable(
                    message=messages.invalid_credential_username_message
                )
            self.instance = credential
            return self.instance
        except models.User.DoesNotExist:
            raise responses.NotFound(message=messages.invalid_username_message)
        except models.Credential.DoesNotExist:
            raise responses.NotFound(message=messages.invalid_credential_message)


class OTPResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    credential = serializers.IntegerField()
    code = serializers.CharField(validators=[validators.Code])
    password = serializers.CharField(max_length=100)

    def save(self):
        try:
            user = models.User.objects.get_by_username(
                username=self.validated_data.get("username")
            )
            credential = models.Credential.objects.get(
                id=self.validated_data.get("credential")
            )
            if credential.user != user:
                raise responses.NotAcceptable(
                    message=messages.invalid_credential_username_message
                )
            self.instance = credential
            return self.instance
        except models.User.DoesNotExist:
            raise responses.NotFound(message=messages.invalid_username_message)
        except models.Credential.DoesNotExist:
            raise responses.NotFound(message=messages.invalid_credential_message)


class ActivationSerializer(serializers.Serializer):
    code = serializers.CharField(validators=[validators.Code])


class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RefreshToken
        fields = ["token"]

    token = serializers.CharField(max_length=40)

    def create(self, validated_data):
        return models.RefreshToken.alives.get(token=validated_data["token"])


class RevokeTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccessToken
        fields = ["token"]

    token = serializers.CharField(max_length=40)

    def create(self, validated_data):
        return models.AccessToken.alives.get(token=validated_data["token"])


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ["id", "title", "user_count", "is_deletable"]


class GroupRetrieveSerializer(GroupListSerializer):
    class Meta:
        model = models.Group
        fields = ["id", "title", "user_count", "is_deletable", "actions"]

    actions = BaseActionSerializer(many=True)


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ["title"]


class GrantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grant
        fields = ["group", "action"]


class ActionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Action
        fields = ["title", "path", "parent"]


class ActionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Action
        fields = ["id", "title", "path", "children"]

    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if obj.children.exists():
            child_serializer = ActionRetrieveSerializer(
                obj.children.all(),
                many=True,
                context=self.context,
            )
            return child_serializer.data
        else:
            return None


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ["id", "created_at", "granted", "user", "action"]

    user = BaseUserSerializer()
    action = BaseActionSerializer()


class ExportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ["id", "created_at", "granted", "user", "action"]

    user = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()

    def get_user(self, obj):
        # BaseUserSerializer should be already imported or defined somewhere
        serializer = BaseUserSerializer(obj.user)
        return serializer.data

    def get_action(self, obj):
        # BaseActionSerializer should be already imported or defined somewhere
        serializer = BaseActionSerializer(obj.action)
        return serializer.data

    def to_representation(self, instance):
        """Flatten the user and action objects into the parent serialization."""
        representation = super().to_representation(instance)
        user_representation = representation.pop('user')
        action_representation = representation.pop('action')

        # Now, flatten the user and action data into the parent serialization
        for key, value in user_representation.items():
            # Prefixing with 'user_' to avoid field name collision
            representation[f'user_{key}'] = value

        for key, value in action_representation.items():
            # Prefixing with 'action_' to avoid field name collision
            representation[f'action_{key}'] = value

        return representation

