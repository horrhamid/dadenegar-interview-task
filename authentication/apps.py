from django.apps import AppConfig

# from . import actions


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    actions = True
    # actions = actions.Actions
