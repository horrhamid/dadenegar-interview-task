from core import models, validators


class Credential(models.Model):
    MOBILE = "mobile"
    EMAIL = "email"
    TYPE_CHOICES = (
        (EMAIL, EMAIL),
        (MOBILE, MOBILE),
    )
    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="credentials",
        related_query_name="credential",
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    credential = models.CharField(max_length=100)

    @property
    def secret_credential(self):
        if self.type == Credential.MOBILE:
            mobile = self.credential
            return mobile[0:2] + "*********" + mobile[-1:]
        else:
            email = self.credential
            return email[0:1] + "******" + email[email.find("@") :]
