from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


# Create your models here.


class AbstractSuperUser(models.Model):
    """
    Abstract base class implementing superuser. Use this when
    you need django-admin without Groups and Permissions.
    """

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def permission_check(self):
        if self.is_superuser:
            return True
        return False

    def has_perm(self, *args, **kwargs):
        return self.permission_check()

    def has_perms(self, *args, **kwargs):
        return self.permission_check()

    def has_module_perms(self, *args, **kwargs):
        return self.permission_check()


class AbstractEmailUser(AbstractBaseUser):
    """ An abstract base class implementing a fully featured User model.
    E-mail address and password are required. By default User is inactive.

    Examples:
        ``
        Basic user model with custom fields:
            class User(AbstractEmailUser):
                first_name = models.CharField()
                last_name = models.CharField()

        Basic user model that works with django-admin.
            class User(AbstractEmailUser, AbstractSuperUser):
                pass

        Basic user model that works with Groups and Permissions:
            class User(AbstractEmailUser, PermissionsMixin)
                pass
        ``
    """

    email = models.EmailField(unique=True, max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')


class User(AbstractSuperUser, AbstractEmailUser):
    pass
