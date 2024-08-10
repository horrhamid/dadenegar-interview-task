from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.urls import re_path, path
from django.contrib import admin

from django.views.static import serve

import re


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        from django.conf import settings
        if settings.ENV.IS_LOCAL:
            schema.schemes = ["http"]
        else:
            schema.schemes = ["https", "http"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="FormFlow API",
        default_version="0.0.1",
    ),
    generator_class=BothHttpAndHttpsSchemaGenerator,
    public=True,
    permission_classes=[AllowAny],
)


def setup_swagger(urlpatterns):
    if settings.ENV.SWAGGER:
        urlpatterns.append(
            re_path(
                r"^swagger/$",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="schema-swagger-ui",
            )
        )
    return urlpatterns


def setup_redoc(urlpatterns):
    if settings.ENV.REDOC:
        urlpatterns.append(
            re_path(
                r"^redoc/$",
                schema_view.with_ui("redoc", cache_timeout=0),
                name="schema-redoc",
            )
        )
    return urlpatterns


def setup_django_admin(urlpatterns):
    if settings.ENV.DJANGO_ADMIN:
        urlpatterns.append(path("admin/", admin.site.urls))
    return urlpatterns


def setup(urlpatterns):
    urlpatterns = setup_swagger(urlpatterns)
    urlpatterns = setup_redoc(urlpatterns)
    urlpatterns = setup_django_admin(urlpatterns)
    return urlpatterns
