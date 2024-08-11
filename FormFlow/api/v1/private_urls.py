from django.urls import path, include

app_name = "private"

urlpatterns = [
    path(
        "authentication/",
        include("authentication.urls.private_urls", namespace="authentication_private"),
    ),
    path(
        "survey/",
        include("survey.urls.private_urls", namespace="survey_private"),
    ),
]
