from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ErrorDetail

from . import messages

OK = 200
CREATED = 201
PARTIAL_CONTENT = 206
ALREADY_REPORTED = 208

MOVED = 301
FOUND = 302

BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
CONFLICT = 409
GONE = 410
TOO_LARGE = 413
UNSUPPORTED_MEDIA_TYPE = 415
TOO_MANY_REQUESTS = 429

SERVER_ERROR = 500
SERVICE_UNAVAILABLE = 503


class Ok(Response):
    status = OK

    def __init__(
        self,
        data=None,
        status=None,
        message: messages.Message = None,
        messages: list = None,
    ):
        if status is None:
            status = self.status
        if message or messages:
            if not data:
                data = {}
            message_list = []
            if message:
                message_list.append(message.as_dict())
            if messages:
                for message in messages:
                    # message_list.append(message.as_dict())
                    message_list.append(message)

            data.update(_messages=message_list)
        super().__init__(data=data, status=status)


class Page(Response):
    pass


class Created(Ok):
    status = CREATED


class PartialContent(Ok):
    status = PARTIAL_CONTENT


class AlreadyReported(Ok):
    status = ALREADY_REPORTED


class Found(Ok):
    status = FOUND

    def __init__(
        self,
        location,
        data=None,
        status=None,
        message: messages.Message = None,
        messages: list = None,
    ):
        super().__init__(data=data, status=status, message=message, messages=messages)
        self["Location"] = location


class BadRequest(Ok, Exception):
    status = BAD_REQUEST

    def __init__(
        self,
        data=None,
        status=None,
        message: messages.Message = None,
        messages: list = None,
    ):
        if status is None:
            status = self.status

        self.status_code = self.status
        super().__init__(data=data, status=status, message=message, messages=messages)


class Conflict(BadRequest):
    status = CONFLICT


class PaymentRequired(BadRequest):
    status = PAYMENT_REQUIRED


class NotFound(BadRequest):
    status = NOT_FOUND


class Forbidden(BadRequest):
    status = FORBIDDEN


class NotAcceptable(BadRequest):
    status = NOT_ACCEPTABLE


class TooManyRequests(BadRequest):
    status = TOO_MANY_REQUESTS


class UnAuthorized(BadRequest):
    status = UNAUTHORIZED


class ServerError(Ok, Exception):
    status = SERVER_ERROR

    def __init__(
        self,
        data=None,
        status=None,
        message: messages.Message = None,
        messages: list = None,
    ):
        if status is None:
            status = self.status

        self.status_code = self.status
        super().__init__(data=data, status=status, message=message, messages=messages)


class ServiceUnavailable(ServerError):
    status = SERVICE_UNAVAILABLE


class WrappedBadRequest(BadRequest):
    def __init__(self, exc: ValidationError):
        message_list = []
        for key in exc.detail:
            value = exc.detail.get(key)
            for error in value:
                if isinstance(error, ErrorDetail):
                    error_message = messages.Message.from_error_detail(error)
                    error_dict = error_message.as_dict()

                elif isinstance(error, dict) and error.get("non_field_errors", None):
                    errors = error.get("non_field_errors")
                    for e in errors:
                        try:
                            error_dict = eval(e)
                        except Exception:
                            error_message = messages.Message.from_error_detail(e)
                            error_dict = error_message.as_dict()
                else:
                    try:
                        error_dict = eval(error)
                    except Exception:
                        error_message = messages.Message.from_error_detail(error)
                        error_dict = error_message.as_dict()
                message_list.append(error_dict)
            # if key != "non_field_errors":
            #     data.update(**{key: message_list})
            # else:
            #     data.update(_messages=message_list)

        super().__init__(messages=message_list, status=exc.status_code)


class WrappedUnAuthorized(UnAuthorized):
    def __init__(self, exc: ValidationError):
        data = {}

        data.update(_messages=[messages.unauthenticated_error.as_dict()])
        super().__init__(data, 401)


class WrappedForbidden(Forbidden):
    def __init__(self, exc: ValidationError):
        data = {}

        data.update(_messages=[messages.forbidden_error.as_dict()])
        super().__init__(data, exc.status_code)
