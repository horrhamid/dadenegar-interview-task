from django.urls import re_path

from .. import views


app_name = "survey_private"
urlpatterns = [
    re_path(
        r"^forms/$",
        views.FormView.as_create_paginate(),
    ),
    re_path(
        r"^questions/$",
        views.QuestionView.as_create_paginate(),
    ),
    re_path(
        r"^answers/$",
        views.AnswerView.as_create_paginate(),
    ),
    re_path(
        r"^responses/$",
        views.ResponseView.as_create_paginate(),
    ),
]