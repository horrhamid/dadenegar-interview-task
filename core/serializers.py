from rest_framework.serializers import *
from rest_framework.serializers import ModelSerializer as RestFrameworkModelSerializer
from . import models


class PercentageDecimalField(DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(max_digits=30, decimal_places=10, *args, **kwargs)

    def validate_precision(self, value):
        return value


class IRRDecimalField(DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(max_digits=30, decimal_places=0, *args, **kwargs)

    def validate_precision(self, value):
        return value


class NestedModelSerializer(ModelSerializer):
    pass


class ModelSerializer(RestFrameworkModelSerializer):
    def get_nested_field_names(self):
        nested_field_names = []
        for field_name in self.get_fields():
            field = self.get_fields().get(field_name)
            if isinstance(field, ListSerializer) and isinstance(
                field.child, NestedModelSerializer
            ):
                nested_field_names.append(field_name)
        return nested_field_names

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for nested_field_name in self.get_nested_field_names():
            attrs.pop(nested_field_name, [])
        return attrs

    def save(self, **kwargs):
        super_return = super().save(**kwargs)
        for nested_field_name in self.get_nested_field_names():
            self.save_nested(nested_field_name)
        return super_return

    def get_nested_queryset(self, key) -> models.QuerySet:
        return getattr(self.instance, key)

    def get_nested_context(self, key) -> dict:
        return {}

    def save_nested(self, key):
        queryset = self.get_nested_queryset(key)
        context = self.get_nested_context(key)
        data_list = self.initial_data.get(key, [])
        SerializerClass = self.get_fields().get(key).child.__class__
        dont_delete_ids = []
        for data in data_list:
            id = data.pop("id", None)
            if id:
                instance = queryset.get(id=id)
                dont_delete_ids.append(id)
            else:
                instance = None
            serializer = SerializerClass(instance, data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dont_delete_ids.append(serializer.instance.id)
        queryset.all().exclude(id__in=dont_delete_ids).delete()
