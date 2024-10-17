from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from users.manager import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=63)
    last_name = models.CharField(_("last name"), max_length=63)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    objects = UserManager()
