from django.core import signing
from django.template.loader import render_to_string
from django.core.mail import send_mail


class BaseActivator:
    """
    Base activator class that implements generating key
    for given value and validating that key.
    """
    def __init__(self, salt=None, max_age=None):
        """
        :param salt: secret key used to sign values
        :param max_age: time in seconds after which value expires
        """
        self.salt = salt
        self.max_age = max_age

    def generate_key(self, value):
        """
        Generate activation key for given string.
        """
        return signing.dumps(
            obj=value,
            salt=self.salt
        )

    def validate_key(self, value):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the value if
        valid or ``None`` if not.
        """
        try:
            value = signing.loads(
                s=value,
                salt=self.salt,
                max_age=self.max_age,
            )
            return value
        # SignatureExpired is a subclass of BadSignature,
        # so this will catch either one.
        except signing.BadSignature:
            return None


class BaseEmailActivator(BaseActivator):
    """
    Base class implementing methods for
    sending activation keys via email.
    """
    email_body_template = ''
    email_subject_template = ''

    def __init__(self, value_to_sign, from_email, to_email, *args, **kwargs):
        super(BaseEmailActivator, self).__init__(*args, **kwargs)
        self.value_to_sign = value_to_sign
        self.from_email = from_email
        self.to_email = to_email

    def get_email_context(self, **kwargs):
        context = {
            'activation_key': self.generate_key(self.value_to_sign),
        }
        context.update(kwargs)
        return context

    def get_email_subject_and_message(self):
        context = self.get_email_context()
        subject = render_to_string(self.email_subject_template, context)
        # Single line to avoid header-injection issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template, context)
        return subject, message

    def send_activation_email(self, **kwargs):
        subject, message = self.get_email_subject_and_message()
        send_mail(
            subject=subject,
            message=message,
            from_email=self.from_email,
            recipient_list=[self.to_email],
            **kwargs
        )

