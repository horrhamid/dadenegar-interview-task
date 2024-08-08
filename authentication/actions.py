from authentication.models import Action, Grant
from authentication.groups import Groups


class Actions:
    authentication = Action(
        path="authentication",
        title="مدیریت اعضا",
    )
    users = Action(
        path="authentication.users",
        title="مدیریت کاربران",
    )
    users_view = Action(
        path="authentication.users.view",
        title="مشاهده کاربران",
    )
    users_create = Action(
        path="authentication.users.create",
        title="افزودن کاربر",
    )
    users_edit = Action(
        path="authentication.users.edit",
        title="ویرایش کاربر",
    )
    users_delete = Action(
        path="authentication.users.delete",
        title="حذف کاربر",
    )
    credentials = Action(
        path="authentication.credentials",
        title="کانال های ورود",
    )
    credentials_view = Action(
        path="authentication.credentials.view",
        title="مشاهده کانال های ورود",
    )
    credentials_create = Action(
        path="authentication.credentials.create",
        title="ایجاد کانال ورود",
    )
    credentials_delete = Action(
        path="authentication.credentials.delete",
        title="حذف کانال ورود",
    )
    groups = Action(
        path="authentication.groups",
        title="گروه های کاربری",
    )
    groups_view = Action(
        path="authentication.groups.view",
        title="مشاهده گروه ها",
    )
    groups_create = Action(
        path="authentication.groups.create",
        title="ایجاد گروه",
    )
    groups_delete = Action(
        path="authentication.groups.delete",
        title="حذف گروه",
    )
    groups_edit = Action(path="authentication.groups.edit", title="ویرایش گروه")
    logs_view = Action(
        path="authentication.logs", title="مشاهذه لاگ", is_loggable=False
    )
