from .base import BaseEmailActivator
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


class UserRegistrationActivator(BaseEmailActivator):
    """
    Activator used for verifying e-mail addresses for new users.
    Given user model instance we will send activation-key to user.email.
    """
    email_body_template = 'registration/email_body.txt'
    email_subject_template = 'registration/email_subject.txt'

    def __init__(self, user=None, request=None):
        super(UserRegistrationActivator, self).__init__(
            value_to_sign=user.email if user else None,
            to_email=user.email if user else None,
            from_email=getattr(settings, 'REGISTRATION_FROM_EMAIL', None),
            max_age=getattr(settings, 'REGISTRATION_MAX_AGE', 86400),
            salt=getattr(settings, 'REGISTRATION_SECRET_KEY', 'default_salt')
        )
        self.request = request

    def get_email_context(self, **kwargs):
        return super(UserRegistrationActivator, self).get_email_context(
            protocol=self.request.scheme,
            site=get_current_site(self.request),
            **kwargs,
        )


class UserPasswordRecoveryActivator(BaseEmailActivator):
    email_body_template = 'recovery/email_body.txt'
    email_subject_template = 'recovery/email_subject.txt'

    def __init__(self, user=None, request=None):
        if user:
            value_to_sign = user.password
        super(UserPasswordRecoveryActivator, self).__init__(
            value_to_sign=user.password if user else None,
            to_email=user.email if user else None,
            from_email=getattr(settings, 'REGISTRATION_FROM_EMAIL', None),
            max_age=getattr(settings, 'PASSWORD_RECOVERY_MAX_AGE', 86400),
            salt=getattr(settings, 'PASSWORD_RECOVERY_SECRET_KEY', 'default_salt')
        )
        self.request = request

    def get_email_context(self, **kwargs):
        return super(UserPasswordRecoveryActivator, self).get_email_context(
            protocol=self.request.scheme,
            site=get_current_site(self.request),
            **kwargs,
        )
