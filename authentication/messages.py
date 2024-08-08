from core.messages import *

register_success_message = Message(
    en="Registered successfully",
    fa="با موفقیت ثبت نام شدید",
    type=Message.SUCCESS,
)
duplicate_username_error = Message(
    en="This username number have already been taken",
    fa="کاربری با این نام کاربری در سیستم ثبت نام شده است.",
    type=Message.ERROR,
)
invalid_login_credentials_message = Message(
    en="Invalid username or password",
    fa="نام کاربری یا رمز عبور اشتباه است",
    type=Message.ERROR,
)
invalid_username_message = Message(
    en="Invalid username",
    fa="نام کاربری اشتباه است",
    type=Message.ERROR,
)
invalid_credential_message = Message(
    en="Invalid credential",
    fa="کد ایمیل یا شماره موبایل اشتباه است",
    type=Message.ERROR,
)
invalid_credential_username_message = Message(
    en="Invalid credential and username",
    fa="کد ایمیل یا شماره موبایل با نام کاربری مطابق نیست",
    type=Message.ERROR,
)
login_success_message = Message(
    en="Loged in successfully",
    fa="با موفقیت وارد شدید",
    type=Message.SUCCESS,
)
invalid_refresh_token_message = Message(
    en="Invalid refresh token",
    fa="توکن وارد شده معتبر نیست",
    type=Message.ERROR,
)
otp_cant_send_message = Message(
    en="Too many requests, You can't receive a code in next 5 seconds",
    fa="به دلیل درخواست مکرر تا ۵ دقیقه امکان ارسال کد وجود ندارد",
    type=Message.ERROR,
)
otp_send_message = Message(
    en="Please enter the received code",
    fa="کد اعتبار سنجی برای شما ارسال شد.",
    type=Message.INFO,
)
otp_no_such_user_message = Message(
    en="No users found with given username",
    fa="کاربری با این شماره موبایل پیدا نشد.",
    type=Message.ERROR,
)
otp_success_message = Message(
    en="Password changed successfully",
    fa="گذرواژه با موفقیت تغییر کرد",
    type=Message.SUCCESS,
)
otp_wrong_message = Message(
    en="Wrong code.",
    fa="کد وارد شده اشتباه است.",
    type=Message.ERROR,
)
otp_cant_try_message = Message(
    en="Too many requests, You can't submit a code in next 5 seconds",
    fa="به دلیل درخواست مکرر تا ۵ دقیقه امکان امتحان کد وجود ندارد",
    type=Message.ERROR,
)

activation_already_activated_message = Message(
    en="User already activated",
    fa="شما قبلا اعتبار سنجی را انجام داده اید!",
    type=Message.INFO,
)
activation_cant_send_message = Message(
    en="Too many requests, You can't receive a code in next 5 seconds",
    fa="به دلیل درخواست مکرر تا ۵ دقیقه امکان ارسال کد وجود ندارد",
    type=Message.ERROR,
)
activation_send_message = Message(
    en="Please enter the received code",
    fa="کد اعتبار سنجی برای شما ارسال شد.",
    type=Message.INFO,
)
activation_cant_try_message = Message(
    en="Too many requests, You can't submit a code in next 5 seconds",
    fa="به دلیل درخواست مکرر تا ۵ دقیقه امکان امتحان کد وجود ندارد",
    type=Message.ERROR,
)

activation_wrong_code_message = Message(
    en="Wrong code.",
    fa="کد وارد شده اشتباه است.",
    type=Message.ERROR,
)
activation_success_message = Message(
    en="Activation done successfully",
    fa="اعتبار سنجی با موفقیت انجام شد",
    type=Message.SUCCESS,
)

logged_out_message = Message(
    en="Logged out successfully",
    fa="از سیستم خارج شدید.",
    type=Message.INFO,
)
password_is_required = Message(
    en="Password is required in creating a user",
    fa="گذرواژه برای ساخت کاربر الزامیست",
    type=Message.ERROR,
)
username_is_required = Message(
    en="Username is required in creating a user",
    fa="نام کاربری برای ساخت کاربر الزامیست",
    type=Message.ERROR,
)
