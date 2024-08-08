import string
from django.utils import timezone
from datetime import timedelta
import random


def random_string(
    length: int = 32, charset: str = string.ascii_letters + string.digits
):
    return "".join(random.choice(charset) for i in range(length))


def future(seconds: int):
    return timezone.now() + timedelta(seconds=seconds)
