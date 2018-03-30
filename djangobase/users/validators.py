"""
Error messages, data and custom validation code used in
django-registration's various user-registration form classes.

"""
from confusable_homoglyphs import confusables
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from . import data

CONFUSABLE = _(u'Popraw błędy...')
CONFUSABLE_EMAIL = _(u'Ten adres e-mail nie może zostać użyty')
RESERVED_NAME = _(u'Popraw błędy...')


class ReservedNameValidator(object):
    """ Validator which disallows many reserved names """
    def __init__(self, reserved_names=data.DEFAULT_RESERVED_NAMES):
        self.reserved_names = reserved_names

    def __call__(self, value):
        # this validator only makes sense when
        # the username field is a string type
        if not isinstance(value, six.text_type):
            return
        if value in self.reserved_names or \
            value.lower() in self.reserved_names or \
           value.startswith('.well-known'):     # https://tools.ietf.org/html/rfc5785
            raise ValidationError(
                RESERVED_NAME, code='reserved_name'
            )


def validate_confusables(value):
    """
    Validator which disallows 'dangerous' usernames likely to
    represent homograph attacks.

    A username is 'dangerous' if it is mixed-script (as defined by
    Unicode 'Script' property) and contains one or more characters
    appearing in the Unicode Visually Confusable Characters file.

    """
    if not isinstance(value, six.text_type):
        return
    if confusables.is_dangerous(value) or \
            confusables.is_dangerous(value.lower()):
        raise ValidationError(CONFUSABLE, code='confusable_value')


def validate_confusables_email(value):
    """
    Validator which disallows 'dangerous' email addresses likely to
    represent homograph attacks.

    An email address is 'dangerous' if either the local-part or the
    domain, considered on their own, are mixed-script and contain one
    or more characters appearing in the Unicode Visually Confusable
    Characters file.

    """
    if '@' not in value:
        return
    local_part, domain = value.split('@')
    if confusables.is_dangerous(local_part) or \
            confusables.is_dangerous(local_part.lower()) or \
            confusables.is_dangerous(domain) or \
            confusables.is_dangerous(domain.lower()):
        raise ValidationError(CONFUSABLE_EMAIL, code='confusable_email')
