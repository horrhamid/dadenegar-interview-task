from rest_framework.exceptions import ErrorDetail


class Message:
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"

    def __init__(self, en: str, fa: str, type: str) -> None:
        self.en = en
        self.fa = fa if fa else en
        self.type = type if type else Message.INFO
        pass

    def as_dict(self):
        return {"en": self.en, "fa": self.fa, "type": self.type}

    def __str__(self) -> str:
        return self.as_dict().__str__()

    @staticmethod
    def from_error_detail(error_detail: ErrorDetail):
        try:
            message = eval(error_detail)
            if isinstance(message, list):
                message = message[0]
            if isinstance(message, ErrorDetail):
                return Message.from_error_detail(message)
            else:
                return Message(
                    en=message.get("en"), fa=message.get("fa"), type=message.get("type")
                )
        except:
            pass
        code = error_detail.code
        en = error_detail
        type = Message.ERROR
        fa = code
        if code == "required":
            fa = "این فیلد الزامی است"
        if code == "unique":
            if en == "A user with that username already exists.":
                fa = "کاربری با این نام کاربری در سیستم وجود دارد"
            else:
                fa = "این فیلد تکراری است"
        # TODO
        return Message(en=en, fa=fa, type=type)


username_error_message = Message(
    "Please enter a valid email or mobile",
    "لطفا شماره موبایل یا ایمیل معتبر وارد کنید.",
    type=Message.ERROR,
)

default_not_found_message = Message(
    en="Instance not found!",
    fa="مورد درخواستی یافت نشد!",
    type=Message.ERROR,
)

default_forbidden_message = Message(
    en="Access to this object is denied!",
    fa="دسترسی به این بخش برای شما امکان پذیر نیست!",
    type=Message.ERROR,
)


default_created_message = Message(
    en="Object created successfully!",
    fa="با موفقیت اضافه شد!",
    type=Message.SUCCESS,
)

default_deleted_message = Message(
    en="Object deleted successfully!",
    fa="با موفقیت حذف شد!",
    type=Message.INFO,
)


default_edited_message = Message(
    en="Object edited successfully!",
    fa="با موفقیت ویرایش شد!",
    type=Message.INFO,
)

mobile_error_message = Message(
    en="Mobile number does not match 09xxxxxxxxx regex",
    fa="شماره موبایل باید ۱۱ رقم و با شروع از ۰۹ باشد",
    type=Message.ERROR,
)
email_error_message = Message(
    en="Email is not valid",
    fa="ایمیل وارد شده معتبر نیست",
    type=Message.ERROR,
)
invalid_jalali_month_day_format = Message(
    en="Jalali month day format must be mm-dd ",
    fa="فورمت روز و ماه شمسی را بطور mm-dd وارد کنید",
    type=Message.ERROR,
)
invalid_jalali_month = Message(
    en="Jalali month should be between 1 and 12",
    fa="ماه باید بین ۱ تا ۱۲ باشد",
    type=Message.ERROR,
)
invalid_jalali_day_first_half = Message(
    en="Jalali day should be between 1 and 31 in first 6 months",
    fa="در ۶ ماه ابتدای سال روز باید بین ۱ تا ۳۱ باشد",
    type=Message.ERROR,
)
invalid_jalali_day_second_half = Message(
    en="Jalali day should be between 1 and 30 in mehr to bahman",
    fa="در ماه های مهر تا بهمن روز باید بین ۱ تا ۳۰ باشد",
    type=Message.ERROR,
)
invalid_jalali_day_esfand = Message(
    en="Jalali day should be between 1 and 29 in esfand",
    fa="در ماه اسفند روز باید بین ۱ تا ۲۹ باشد",
    type=Message.ERROR,
)
code_error_message = Message(
    en="Code must be 6 digits number",
    fa="کد اعتبار سنجی باید ۶ رقم باشد",
    type=Message.ERROR,
)
national_id_error_message = Message(
    en="National code should be 10 digits number.",
    fa="کد ملی باید یک عدد ۱۰ رقمی باشد",
    type=Message.ERROR,
)
duplicate_mobile_error = Message(
    en="This mobile number have already been taken",
    fa="کاربری با این شماره موبایل در سیستم ثبت نام شده است.",
    type=Message.ERROR,
)
unauthenticated_error = Message(
    en="Authentication failure",
    fa="برای دسترسی به این بخش باید وارد شوید.",
    type=Message.ERROR,
)
forbidden_error = Message(
    en="Not authorized to preform this action.",
    fa="شما به این بخش دسترسی ندارید",
    type=Message.ERROR,
)
cant_change_status_error = Message(
    en="Status can not be changed.",
    fa="وضعیت نمیتواند تغییر کند",
    type=Message.ERROR,
)
investor_not_found_message = Message(
    en="Investor not found!",
    fa="سرمایه گذار یافت نشد!",
    type=Message.ERROR,
)
cancel_request_fail_invalid_unit_count = Message(
    en="Number of cancel request is greater than investor units.",
    fa="تعداد واحدهای درخواستی بیشتر از تعداد واحد های سرمایه گذار است.",
    type=Message.ERROR,
)
no_data = Message(
    en="No data!",
    fa="داده ای وجود ندارد!",
    type=Message.ERROR,
)