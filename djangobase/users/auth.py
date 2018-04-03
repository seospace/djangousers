from django.contrib.auth.backends import ModelBackend
from .managers import UserManager


class EmailBackend(ModelBackend):
    """
    Authentication backend for email as USERNAME_FIELD.
    We just normalize the email before authenticating.
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        if email:
            username = email
        if username:
            username = UserManager.normalize_email(username)
        return super(EmailBackend, self).authenticate(request, username, password, **kwargs)
