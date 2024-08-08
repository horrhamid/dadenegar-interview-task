from collections.abc import Iterable, Sequence
from typing import Any
from django.db.models import *
from django.db.models import Model as DjangoModel, Manager as DjangoManager
from .builders import *
from django.utils import timezone
import uuid
from django.db.models import Sum


class AbsoluteSum(Sum):
    name = 'AbsoluteSum'
    template = '%(function)s(%(absolute)s(%(expressions)s))'

    def __init__(self, expression, **extra):
        super(AbsoluteSum, self).__init__(
            expression, absolute='ABS ', output_field=IntegerField(), **extra)

    def __repr__(self):
        return "SUM(ABS(%s))".format(
            self.arg_joiner.join(str(arg) for arg in self.source_expressions)
        )


class PercentageField(FloatField):
    def __int__(self, *args, **kwargs):
        self.min_value = 0
        self.max_value = 1
        super().__init__(*args, **kwargs)


class StandardDecimal(DecimalField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.update(decimal_places=5)
        kwargs.update(max_digits=30)
        super().__init__(*args, **kwargs)


class Manager(DjangoManager):
    use_in_migrations = True

    def bulk_update(
        self, objs: Iterable, fields: Sequence[str], batch_size: int | None = None
    ) -> int:
        i = 0
        for obj in objs:
            obj.pre_save(in_create=False, in_bulk=True, index=i)
            i += 1

        instances = super().bulk_update(objs, fields, batch_size)
        i = 0
        for obj in objs:
            obj.post_save(in_create=False, in_bulk=True, index=i)
            i += 1

        return instances

    def parent_bulk_create(self, objs):
        return super().bulk_create(objs)

    def bulk_create(self, objs, *args, **kwargs) -> None:
        if len(objs) == 0:
            return []
        i = 0
        for obj in objs:
            obj.pre_save(in_create=True, in_bulk=True, index=i)
            i += 1
        the_class = None
        has_same_classes = True
        for obj in objs:
            if the_class is None:
                the_class = obj.__class__
            else:
                if obj.__class__ != the_class:
                    has_same_classes = False
        if not has_same_classes:
            grouped_lists = {}
            for obj in objs:
                obj_class = obj.__class__
                grouped_lists.setdefault(obj_class, [])
                class_list = grouped_lists.get(obj_class)
                class_list.append(obj)
            for obj_class in grouped_lists:
                obj_list = grouped_lists.get(obj_class)
                obj_class.objects.bulk_create(obj_list)
        else:
            current_model = the_class
            model_sequence = []
            while current_model:
                model_sequence.append(current_model)
                current_model = current_model._meta.pk.related_model

            main_model = model_sequence.pop()
            main_model_local_fields = main_model._meta.local_fields
            main_model_objects = []
            for obj in objs:
                main_model_kwargs = {}
                for field in main_model_local_fields:
                    value = getattr(obj, field.name)
                    main_model_kwargs.update(**{field.name: value})


                main_obj = main_model(**main_model_kwargs)
                main_model_objects.append(main_obj)

            result = main_model.objects.parent_bulk_create(main_model_objects)
            for main_object, obj in zip(main_model_objects, objs):

                obj.pk = main_object.pk
            while len(model_sequence) > 0:
                model = model_sequence.pop()
                for obj in objs:
                    setattr(obj, model._meta.pk.name + "_id", obj.pk)
                model_local_fields = model._meta.local_fields
                queryset = QuerySet(model)
                queryset._for_write = True
                result = queryset._batched_insert(
                    objs,
                    model_local_fields,
                    batch_size=None,
                )
            i = 0
            for instance in objs:
                instance.post_save(in_create=True, in_bulk=True, index=i)
                i += 1
            return result


class Model(DjangoModel):
    class Meta:
        abstract = True

    objects = Manager()

    def pre_save(self, in_create=False, in_bulk=False, index=None) -> None:
        pass

    def post_save(self, in_create=False, in_bulk=False, index=None) -> None:
        pass

    def save(self, *args, **kwargs):
        in_create = self.pk is None
        self.pre_save(in_create=in_create, in_bulk=False)
        super().save(*args, **kwargs)
        self.post_save(in_create=in_create, in_bulk=False)


def today():
    from django.utils import timezone

    return timezone.now().date()


def now():
    from django.utils import timezone

    return timezone.now()


def today_time(hour=0, minute=0, second=0):
    return day_time(today(), hour, minute, second)


def day_time(date, hour=0, minute=0, second=0):
    from datetime import datetime, time, timedelta
    import pytz

    _time = time(hour=hour, minute=minute, second=second)
    navie_combined = datetime.combine(date, _time)
    return pytz.timezone("Asia/Tehran").localize(navie_combined)


def day_start(date):
    import datetime

    return datetime.datetime.combine(
        date,
        datetime.time(hour=0, minute=0, second=0, tzinfo=timezone.LocalTimezone.tzname),
    )


def day_end(date):
    import datetime

    return datetime.datetime.combine(
        date,
        datetime.time(
            hour=24, minute=0, second=0, tzinfo=timezone.LocalTimezone.tzname
        ),
    )


class UUIDModel(Model):
    class Meta:
        abstract = True

    uuid = UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)


class CreatableModel(Model):
    class Meta:
        abstract = True

    created_at = DateTimeField(default=timezone.now, editable=False)


class UpdatableModel(Model):
    class Meta:
        abstract = True

    updated_at = DateTimeField(null=True, blank=True, default=None)

    def save(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class ActivableActiveManager(Manager):
    pass
    # def get_queryset(self) -> QuerySet:
    #     return super().get_queryset().filter(is_active=True)


class ActivableModel(Model):
    actives = ActivableActiveManager()
    objects = Manager()

    class Meta:
        abstract = True

    is_active = BooleanField(default=True)

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()


class DeletableAliveManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(deleted_at=None)


class DeletableModel(Model):
    objects = Manager()
    alives = DeletableAliveManager()

    class Meta:
        abstract = True

    deleted_at = DateTimeField(null=True, blank=True, default=None)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()


class OrderedModel(Model):
    class Meta:
        abstract = True
        ordering = ["order"]

    order = FloatField(default=0)


class AuditableModel(CreatableModel, UpdatableModel, DeletableModel):
    class Meta:
        abstract = True


class SuperModel(AuditableModel, OrderedModel, UUIDModel):
    class Meta:
        abstract = True


class DataModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
