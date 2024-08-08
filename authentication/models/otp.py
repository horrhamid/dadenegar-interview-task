import string
from authentication import constants
from core import models, sms, validators, email
import datetime


def default_otp_code():
    return models.random_string(6, string.digits)


class OTPManager(models.Manager):
    def get_for_credential(self, credential):
        instance, _ = self.get_or_create(
            credential=credential, defaults={"credential": credential}
        )
        return instance


class OTP(models.Model):
    objects = OTPManager()
    credential = models.ForeignKey(
        to="authentication.Credential", on_delete=models.CASCADE
    )
    code = models.CharField(
        max_length=6, validators=[validators.Code], default=default_otp_code
    )
    send_count = models.IntegerField(default=0)
    tried_count = models.IntegerField(default=0)
    last_send = models.DateTimeField(null=True, default=None)
    last_tried = models.DateTimeField(null=True, default=None)

    def can_try(self):
        if (
            not self.last_tried
            or self.last_tried
            + datetime.timedelta(seconds=constants.BLOCK_TIME_SECONDS)
            < models.now()
        ):
            self.tried_count = 0
            self.last_tried = None
            self.save()
        return self.tried_count < constants.OTP_MAX_TRY_COUNT

    def can_send(self):
        if not self.last_send or (
            self.last_send + datetime.timedelta(seconds=constants.BLOCK_TIME_SECONDS)
            < models.now()
        ):
            self.send_count = 0
            self.last_send = None
            self.save()
        return self.send_count < constants.OTP_MAX_SEND_COUNT

    def try_code(self, code: str):
        self.last_tried = models.now()
        self.tried_count += 1
        self.save()
        is_valid = self.code == code
        if is_valid:
            self.delete()
        return is_valid

    def send_code(self):
        self.last_send = models.now()
        from .credential import Credential

        receptor = self.credential.credential
        if self.credential.type == Credential.MOBILE:
            sms.send_sms(receptor, {"type": "otp", "code": self.code})
        else:
            email.send_email(receptor, {"type": "otp", "code": self.code})
        self.send_count += 1
        self.save()
