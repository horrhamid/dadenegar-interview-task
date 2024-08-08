from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.tasks import check_access


def ActionPermission(obj):
    from authentication.models import Action

    class PermissionClass(IsAuthenticated):
        def has_permission(self, request, view):
            super_permission = super().has_permission(request, view)
            if not super_permission:
                return False
            if isinstance(obj, str):
                path_regex = obj
            elif isinstance(obj, Action):
                path_regex = obj.path
            else:
                sub_object = obj.get(view.action, None)
                if isinstance(sub_object, Action):
                    path_regex = sub_object.path
                else:
                    path_regex = sub_object
            return check_access(
                user=request.user, path_regex=path_regex, kwargs=view.kwargs
            )

    return PermissionClass


def CRUDActionPermission(obj):
    from authentication.models import Action

    if isinstance(obj, str):
        path_prefix = obj
    elif isinstance(obj, Action):
        path_prefix = obj.path

    path_dict = {
        "create": path_prefix + ".create",
        "delete": path_prefix + ".delete.<pk>",
        "edit": path_prefix + ".edit.<pk>",
        "find": path_prefix + ".view",
        "list": path_prefix + ".view",
        "paginate": path_prefix + ".view",
        # "export_to_excel": path_prefix + ".view",
        "retrieve": path_prefix + ".view.<pk>",
    }
    return ActionPermission(path_dict)
