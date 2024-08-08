from django.conf import settings
from django.urls import path, include

app_name = "v1"

urlpatterns = [
    path(
        "private/",
        include("FormFlow.api.v1.private_urls", namespace="private"),
    )
]
