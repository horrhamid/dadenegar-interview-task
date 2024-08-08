from . import messages
import re
from rest_framework.exceptions import ValidationError as DjangoValidationError
from core import responses


class ValidationError(DjangoValidationError):
    message: messages.Message = None

    def __init__(self, message: messages.Message):
        self.message = message.as_dict()
        super().__init__(message.as_dict().__str__())


def Mobile(value):
    regex = r"^09[0-9]{9}$"
    message = messages.mobile_error_message

    if value:
        if not re.match(regex, value):
            raise ValidationError(message)


def Email(value):
    regex = r"^\S+@\S+\.\S+$"
    message = messages.email_error_message

    if value:
        if not re.match(regex, value):
            raise ValidationError(message)


def JalaliMonthDay(value):
    regex = r"^[0-9]{2}-[0-9]{2}$"
    if value:
        if not re.match(regex, value):
            raise ValidationError(messages.invalid_jalali_month_day_format)
        month = int(value[0 : value.find("-")])
        day = int(value[value.find("-") + 1 :])
        if month < 1 or month > 12:
            raise ValidationError(messages.invalid_jalali_month)
        if month in [1, 2, 3, 4, 5, 6] and (day < 1 or day > 31):
            raise ValidationError(messages.invalid_jalali_day_first_half)
        if month in [7, 8, 9, 10, 11] and (day < 1 or day > 30):
            raise ValidationError(messages.invalid_jalali_day_second_half)
        if month == 12 and (day < 1 or day > 29):
            raise ValidationError(messages.invalid_jalali_day_esfand)


def Code(value):
    regex = r"[0-9]{6}$"
    message = messages.code_error_message

    if value:
        if not re.match(regex, value):
            raise ValidationError(message)


def NationalID(value):
    regex = r"^[0-9]{10}$"
    message = messages.national_id_error_message

    if value:
        if not re.match(regex, value):
            raise ValidationError(message)
        parity = int(value[9])
        sum_of_products = 0
        for i in range(9):
            sum_of_products += int(value[i]) * (10 - i)
        actual_parity = sum_of_products % 11
        if actual_parity < 2:
            actual_parity = actual_parity
        else:
            actual_parity = 11 - actual_parity
        if actual_parity != parity:
            raise ValidationError(message)


def NotIn(queryset, field, message):
    def Validator(value):
        if value and queryset.filter(**{field: value}).exists():
            raise ValidationError(message)
            # raise responses.BadRequest(message=message)

    return Validator


def UniqueMobile(value):
    from authentication.models import User

    if User.objects.filter(mobile=value).exists():
        raise ValidationError(messages.duplicate_mobile_error)
