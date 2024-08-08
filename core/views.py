from rest_framework.viewsets import ViewSet as DjangoViewSet

from rest_framework import serializers
from . import messages, models, responses
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework import exceptions
from openpyxl import Workbook

from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg import openapi
from drf_yasg.utils import (
    filter_none,
    force_real_str,
)


class MySchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys
        path = self.path.split("/")
        api = path[2]
        app = path[3]
        view = self.view.__class__.__name__
        action = self.view.action
        return f"{api}_{app}_{view}_{action}"

    def get_tags(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys
        path = self.path.split("/")
        api = path[2]
        app = path[3]
        return [f"{api}_{app}"]

    def get_default_response_serializer(self):
        serializer_class = self.view.get_response_serializer()
        if serializer_class:
            return serializer_class()
        else:
            return super().get_view_serializer()

    def get_request_serializer(self):
        serializer_class = self.view.get_request_serializer()
        if serializer_class:
            return serializer_class()
        else:
            return super().get_view_serializer()

    def get_query_parameters(self):
        if self.get_method() == "get":
            from drf_yasg import openapi

            QuerySerializer = self.view.get_query_serializer()
            if QuerySerializer:
                return self.serializer_to_parameters(
                    QuerySerializer(), openapi.IN_QUERY
                )
            else:
                RequestSerializer = self.view.get_request_serializer()
                if RequestSerializer:
                    return self.serializer_to_parameters(
                        RequestSerializer(), openapi.IN_QUERY
                    )
                else:
                    return []
        else:
            return super().get_query_parameters()

    def get_produces(self):
        return super().get_produces()

    def get_method(self):
        method = None
        for m, action in self.view.action_map.items():
            if action == self.view.action:
                method = m
        return method

    def get_request_body_parameters(self, consumes):
        if self.get_method() in ["get"]:
            return []
        return super().get_request_body_parameters(consumes)

    def get_default_responses(self):
        default_schema = ""
        action = self.view.action
        response_serializer = self.get_default_response_serializer()
        if response_serializer:
            default_schema = self.serializer_to_schema(response_serializer)
        if action == "create":
            return {responses.CREATED: "Create message"}
        else:
            return {responses.OK: default_schema}


class BaseViewSet(DjangoViewSet):
    swagger_schema = MySchema
    permission_classes = []
    request_serializer: serializers.Serializer | dict = None
    response_serializer: serializers.Serializer | dict = None
    base_queryset: models.QuerySet | dict | None = None

    ordering_field: str | None = "ordering"
    search_field: str | None = "search"
    limit_field: str | None = "limit"

    ordering_choices: list | str | None | dict = None
    search_lookups: list | str | None = None
    limit_max_value: int | None = None

    default_ordering: str | None = None
    default_limit: int | None = None

    filter_lookups: list | str | None | dict = None

    @property
    def allowed_filtering(self):
        return len(self.filter_lookups_dict.keys()) > 0

    @property
    def filter_lookups_dict(self) -> dict:
        if self.filter_lookups is None:
            return {}
        if isinstance(self.filter_lookups, str):
            return {self.filter_lookups: self.filter_lookups}
        if isinstance(self.filter_lookups, list):
            d = {}
            for item in self.filter_lookups:
                d.update(**{item: item})

            return d
        if isinstance(self.filter_lookups, dict):
            return self.filter_lookups

    @property
    def allowed_ordering(self):
        return (self.ordering_field is not None) and len(
            self.ordering_choices_dict.keys()
        ) >= 1

    @property
    def ordering_choices_dict(self):
        if self.ordering_choices is None:
            return {}
        if isinstance(self.ordering_choices, str):
            return {self.ordering_choices: self.ordering_choices}
        if isinstance(self.ordering_choices, list):
            d = {}
            for item in self.ordering_choices:
                d.update(**{item: item})
            return d
        if isinstance(self.ordering_choices, dict):
            return self.ordering_choices

    @property
    def validated_ordering(self):
        if self.allowed_ordering:
            ordering_field = self.request.query_params.get(self.ordering_field, None)
            if ordering_field in self.ordering_choices_dict.keys():
                return self.ordering_choices_dict.get(ordering_field)
            return self.default_ordering

    @property
    def allowed_search(self):
        return (self.search_field is not None) and len(self.search_lookups_list) >= 1

    @property
    def search_lookups_list(self):
        if isinstance(self.search_lookups, str):
            return [self.search_lookups]
        if isinstance(self.search_lookups, list):
            return self.search_lookups
        return []

    @property
    def validated_search(self):
        if self.allowed_search:
            return self.request.query_params.get(self.search_field, None)

    @property
    def allowed_limit(self):
        return self.limit_field and self.limit_max_value

    @property
    def validated_limit(self):
        if self.allowed_limit:
            try:
                limit = int(self.request.query_params.get(self.limit_field, 0))
                if limit == 0:
                    limit = None
            except ValueError:
                limit = None
            if limit:
                if self.limit_max_value and self.limit_max_value < limit:
                    return self.default_limit
                return limit
            else:
                return self.default_limit
        else:
            return self.default_limit

    def get_request_serializer(self) -> serializers.Serializer:
        if isinstance(self.request_serializer, dict):
            return self.request_serializer.get(self.action)
        return self.request_serializer

    def get_query_fields(self) -> OrderedDict:
        if self.action in ["list", "paginate", "find"]:
            fields = OrderedDict()
            if self.allowed_ordering:
                choices = []
                for choice in self.ordering_choices_dict.keys():
                    choices.append(choice)
                fields.update(
                    **{
                        self.ordering_field: serializers.ChoiceField(
                            choices=choices,
                            required=False,
                            default=self.default_ordering,
                        )
                    }
                )
            if self.allowed_search:
                fields.update(
                    **{
                        self.search_field: serializers.CharField(
                            required=False, default=None, allow_blank=True
                        )
                    }
                )
            if self.allowed_limit:
                fields.update(
                    **{
                        self.limit_field: serializers.IntegerField(
                            required=False, default=None
                        )
                    }
                )
            if self.allowed_filtering:
                for param_name in self.filter_lookups_dict.keys():
                    field_name = self.filter_lookups_dict.get(param_name)
                    is_list = field_name is not None and field_name.endswith("__in")
                    if is_list:
                        fields.update(
                            **{
                                param_name: serializers.ListField(
                                    child=serializers.CharField(),
                                    required=False,
                                    default=[],
                                )
                            }
                        )
                    else:
                        fields.update(
                            **{
                                param_name: serializers.CharField(
                                    required=False, default=None, allow_blank=True
                                )
                            }
                        )
            return fields
        return None

    def get_query_serializer(self) -> serializers.Serializer:
        query_fields = self.get_query_fields()
        if query_fields:

            class QuerySerializerMeta(serializers.SerializerMetaclass):
                @classmethod
                def _get_declared_fields(cls, bases, attrs):
                    return self.get_query_fields()

            class QuerySerializer(
                serializers.Serializer, metaclass=QuerySerializerMeta
            ):
                class Meta:
                    ref_name = self.__class__.__name__ + "QuerySerializer"

            return QuerySerializer

    def get_response_serializer(self) -> serializers.Serializer:
        if isinstance(self.response_serializer, dict):
            return self.response_serializer.get(self.action)
        return self.response_serializer

    def handle_exception(self, exc):
        if isinstance(exc, exceptions.PermissionDenied):
            if not self.request.user or not self.request.user.is_authenticated:
                return responses.WrappedUnAuthorized(exc)

            return responses.WrappedForbidden(exc)
        if isinstance(exc, exceptions.ValidationError):
            return responses.WrappedBadRequest(exc)
        if isinstance(
            exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)
        ):
            return responses.WrappedUnAuthorized(exc)

        return super().handle_exception(exc)

    def get_serializer_context(self):
        return {"request": self.request, "view": self}

    def get_base_queryset(self) -> models.QuerySet:
        if self.base_queryset is None:
            raise Exception("You should provide a queryset to this view")
        if isinstance(self.base_queryset, models.QuerySet):
            return self.base_queryset.all()
        if isinstance(self.base_queryset, dict):
            return self.base_queryset.get(self.action).all()

    def get_filtered_queryset(self):
        queryset = self.get_base_queryset()
        if self.allowed_filtering:
            field_values = {}
            for param_name in self.filter_lookups_dict:
                field_name = self.filter_lookups_dict.get(param_name)

                if field_name.endswith("__in"):
                    value = self.request.query_params.get(param_name, None)
                    if value:
                        value = value.split(",")
                else:
                    value = self.request.query_params.get(param_name, None)
                if value:
                    if value == "true":
                        value = True
                    if value == "false":
                        value = False
                    if value == "null":
                        value = None
                    field_values.update(**{field_name: value})
            return queryset.filter(**field_values).distinct()
        else:
            return queryset

    def get_searched_queryset(self):
        queryset = self.get_filtered_queryset()
        search = self.validated_search
        if search:
            from django.db.models import functions

            values = []
            for search_lookup in self.search_lookups_list:
                values.extend([search_lookup, models.Value(" ")])
            return queryset.annotate(
                **{
                    self.search_field: functions.Concat(
                        *values, output_field=models.TextField()
                    )
                }
            ).filter(**{f"{self.search_field}__icontains": search})
        else:
            return queryset

    def get_ordered_queryset(self):
        queryset = self.get_searched_queryset()
        ordering = self.validated_ordering
        if ordering:
            return queryset.order_by(ordering)
        else:
            return queryset

    def get_limited_queryset(self):
        queryset = self.get_ordered_queryset()
        limit = self.validated_limit
        if limit:
            return queryset[:limit]
        else:
            return queryset

    def get_queryset(self):
        return self.get_limited_queryset()

    def get_object(
        self,
        queryset: models.QuerySet = None,
        keyword: str = "pk",
        lookup_field: str = "pk",
    ):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(**{lookup_field: self.kwargs.get(keyword, None)})
            self.check_object_permissions(self.request, obj)
            return obj
        except ObjectDoesNotExist:
            raise responses.NotFound(message=self.get_not_found_message())

    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            if permission.has_object_permission(request, self, obj):
                return True
        raise responses.Forbidden(message=self.get_forbidden_message(obj))

    def get_forbidden_message(self, instance=None):
        return messages.default_forbidden_message

    def get_not_found_message(self, instance=None):
        return messages.default_not_found_message

    def get_create_message(self, instance=None):
        return messages.default_created_message

    def get_edit_message(self, instance=None):
        return messages.default_edited_message

    def get_delete_message(self, instance=None):
        return messages.default_deleted_message

    @classmethod
    def as_edit_delete_retrieve(cls):
        return cls.as_view({"post": "edit", "delete": "delete", "get": "retrieve"})

    @classmethod
    def as_delete_retrieve(cls):
        return cls.as_view({"delete": "delete", "get": "retrieve"})

    @classmethod
    def as_delete(cls):
        return cls.as_view({"delete": "delete"})

    @classmethod
    def as_edit_retrieve(cls):
        return cls.as_view({"post": "edit", "get": "retrieve"})

    @classmethod
    def as_edit(cls):
        return cls.as_view({"post": "edit"})

    @classmethod
    def as_create_list(cls):
        return cls.as_view({"post": "create", "get": "list"})

    @classmethod
    def as_create_paginate(cls):
        return cls.as_view({"post": "create", "get": "paginate"})

    @classmethod
    def as_create(cls):
        return cls.as_view({"post": "create"})

    @classmethod
    def as_retrieve(cls):
        return cls.as_view({"get": "retrieve"})

    @classmethod
    def as_list(cls):
        return cls.as_view({"get": "list"})

    @classmethod
    def as_paginate(cls):
        return cls.as_view({"get": "paginate"})

    @classmethod
    def as_export_to_excel(cls):
        return cls.as_view({"get": "export_to_excel"})


class RetrieveModelMixin(BaseViewSet):
    @action(detail=True, methods=["GET"])
    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            serializer_class = self.get_response_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(obj, context=serializer_context)
            data = serializer.data
            return responses.Ok(data)
        except ObjectDoesNotExist:
            return responses.NotFound(message=self.get_not_found_message())
        except responses.BadRequest as response:
            return response


class FindModelMixin(BaseViewSet):
    @action(detail=True, methods=["GET"])
    def find(self, request, *args, **kwargs):
        try:
            obj = self.find_object()
            serializer_class = self.get_response_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(obj, context=serializer_context)
            data = serializer.data
            return responses.Ok(data)
        except responses.BadRequest as response:
            return response

    def find_object(self):
        try:
            obj = self.get_queryset().first()
            self.check_object_permissions(self.request, obj)
            return obj
        except ObjectDoesNotExist:
            raise responses.NotFound(message=self.get_not_found_message())


class ListModelMixin(BaseViewSet):
    @action(detail=True, methods=["GET"])
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            for obj in queryset:
                try:
                    self.check_object_permissions(self.request, obj)
                except Exception as error:
                    raise error

            serializer_class = self.get_response_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(
                queryset, many=True, context=serializer_context
            )
            data = serializer.data
            return responses.Ok(data)
        except responses.BadRequest as response:
            return response


class PaginateModelMixin(BaseViewSet):
    page_number_field = "page_number"

    page_size_field = "page_size"
    allow_page_size: bool = False
    default_page_size = 10
    min_allowed_page_size = 5
    max_allowed_page_size = 100

    @property
    def validated_page_number(self):
        page_number = 1
        try:
            page_number = int(self.request.query_params.get(self.page_number_field, 0))
            if page_number <= 0:
                page_number = 1
        except ValueError:
            pass
        return page_number

    @property
    def allowed_page_size(self):
        return self.page_size_field and self.allow_page_size

    def get_query_fields(self):
        fields = super().get_query_fields()
        if self.action == "paginate":
            fields.update(
                **{
                    self.page_number_field: serializers.IntegerField(
                        required=False, default=1
                    )
                }
            )
            if self.allow_page_size:
                fields.update(
                    **{
                        self.page_size_field: serializers.IntegerField(
                            required=False,
                            default=self.default_page_size,
                            min_value=self.min_allowed_page_size,
                            max_value=self.max_allowed_page_size,
                        )
                    }
                )
        return fields

    @action(detail=True, methods=["GET"])
    def paginate(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            start_index = (self.validated_page_number - 1) * self.get_page_size()
            end_index = self.validated_page_number * self.get_page_size()

            instances = queryset[start_index:end_index]
            for obj in instances:
                try:
                    self.check_object_permissions(self.request, obj)
                except Exception as error:
                    raise error
            serializer_class = self.get_response_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(
                instances, many=True, context=serializer_context
            )
            data = serializer.data
            return responses.Ok(
                {
                    "results": data,
                    self.page_size_field: self.get_page_size(),
                    "page_count": self.get_page_count(),
                    "count": self.get_queryset().count(),
                    self.page_number_field: self.validated_page_number,
                    **self.get_additional_pagination_fields(instances, queryset),
                }
            )

        except responses.BadRequest as response:
            return response

    def get_header_mapping(self):
        return {}

    @action(detail=False, methods=['GET'])
    def export_to_excel(self, request, *args, **kwargs):
        from django.http import HttpResponse
        queryset = self.get_queryset()
        serializer_context = self.get_serializer_context()
        serializer_class = self.get_response_serializer()
        serializer = serializer_class(
            queryset, many=True, context=serializer_context
        )
        header_mapping = self.get_header_mapping()
        wb = Workbook()
        ws = wb.active
        data = serializer.data
        if data:
            if len(header_mapping) > 0:
                headers = [header_mapping.get(header, header) for header in data[0].keys()]
            else:
                headers = data[0].keys()
            ws.append(list(headers))

            for item in data:
                ws.append(list(item.values()))

            # Save the excel file to a response
            response = HttpResponse(content_type='openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="your_model_data.xlsx"'
            wb.save(response)

            return response
        else:
            return responses.BadRequest(
                message=messages.no_data
            )

    def get_additional_pagination_fields(self, instances, queryset):
        return {}

    def get_page_size(self):
        if self.allowed_page_size:
            try:
                page_size = int(self.request.query_params.get(self.page_size_field, 0))
            except ValueError:
                page_size = 0
            if (
                page_size < self.min_allowed_page_size
                or page_size > self.max_allowed_page_size
            ):
                page_size = self.default_page_size
            return page_size
        else:
            return self.default_page_size

        return page

    def get_page_count(self):
        count = self.get_queryset().count()
        page_count = int(count / self.get_page_size()) + 1
        if count % self.get_page_size() == 0:
            page_count -= 1
        return page_count


class CreateModelMixin(BaseViewSet):
    @action(detail=False, methods=["POST"])
    def create(self, request, *args, **kwargs):
        try:
            serializer_class = self.get_request_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(
                context=serializer_context, data=self.request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return responses.Created(
                message=self.get_create_message(serializer.instance)
            )
        except responses.BadRequest as response:
            return response


class EditModelMixin(BaseViewSet):
    @action(detail=True, methods=["POST"])
    def edit(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            self.check_object_permissions(self.request, obj)
            serializer_class = self.get_request_serializer()
            serializer_context = self.get_serializer_context()
            serializer = serializer_class(
                obj, context=serializer_context, data=self.request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return responses.Ok(message=self.get_edit_message(serializer.instance))
        except ObjectDoesNotExist:
            return responses.NotFound(message=self.get_not_found_message())
        except responses.BadRequest as response:
            return response


class DeleteModelMixin(BaseViewSet):
    def check_delete_conditions(self, obj):
        return obj.deleted_at is None

    @action(detail=True, methods=["DELETE"])
    def delete(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            self.check_object_permissions(self.request, obj)
            self.check_delete_conditions(obj)
            obj.delete()
            return responses.Ok(message=self.get_delete_message(obj))
        except ObjectDoesNotExist:
            return responses.NotFound(message=self.get_not_found_message())
        except responses.BadRequest as response:
            return response
