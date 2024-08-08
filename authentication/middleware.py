from django.utils.deprecation import MiddlewareMixin
from . import models
from django.utils import timezone

from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import BaseAuthentication


def get_user(request):
    token = request.headers.get("Authorization", None)
    token = request.headers.get("authorization", token)

    if token and token.startswith("Bearer "):
        token = token[7:]
    token = models.AccessToken.objects.get(token=token)
    request._cached_user = token.user
    return request._cached_user


class TokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)

        authorization_token = request.headers.get("Authorization", None)
        authorization_token = request.headers.get("authorization", authorization_token)

        if authorization_token and authorization_token.startswith("Bearer "):
            authorization_token = authorization_token[7:]
        if models.AccessToken.objects.filter(
            token=authorization_token, deleted_at=None, expire_at__gt=timezone.now()
        ).exists():
            access_token = models.AccessToken.objects.get(token=authorization_token)
            request._chached_user = access_token.user
            request.user = access_token.user
            request.user = SimpleLazyObject(lambda: get_user(request))


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)

        authorization_token = request.headers.get("Authorization", None)
        authorization_token = request.headers.get("authorization", authorization_token)
        if authorization_token and authorization_token.startswith("Bearer "):
            authorization_token = authorization_token[7:]
        if models.AccessToken.objects.filter(
            token=authorization_token, deleted_at=None, expire_at__gt=timezone.now()
        ).exists():
            access_token = models.AccessToken.objects.get(token=authorization_token)
            request._chached_user = access_token.user
            request.user = access_token.user
            request.user = SimpleLazyObject(lambda: get_user(request))
            return (access_token.user, authorization_token)
        else:
            return (None, None)
