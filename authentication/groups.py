from .models import Group


class Groups:
    managers = Group(key="managers", title="مدیران")
    operators = Group(key="operators", title="کاربران ثبت - مرکزی")
    branch_operators = Group(key="branch_operators", title="کاربران ثبت - شعب")
    auditors = Group(key="auditors", title="حسابرس ها")
    proctors = Group(key="proctors", title="متولیان")
    inspectors = Group(key="inspectors", title="سازمان بورس - مشاهده")
    super_inspectors = Group(key="super_inspectors", title="سازمان بورس - مدیریت")
