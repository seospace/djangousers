from django.test import TestCase, SimpleTestCase
from django import forms
from .. import validators
from .. import data


class ValidatorsTestCase(SimpleTestCase):
    def setUp(self):
        self.reserved_names = data.DEFAULT_RESERVED_NAMES
        self.consfusables = [
            'Alloρ',
            'ΑlaskaJazz',
            u'p\u0430yp\u0430l',
            u'g\u043e\u043egle',
            u'\u03c1ay\u03c1al',
        ]
        self.consfusables_emails = [
            'Alloρ@o2.pl',
            'ΑlaskaJazz@domain.com',
            u'p\u0430yp\u0430l@example.com',
            u'g\u043e\u043egle@example.com',
            u'\u03c1y\u03c1al@example.com',
            u'paypal@ex\u0430mple.com',
            u'google@exam\u03c1le.com',
        ]
        self.valid_data = {
            'email': 'alice@example.com',
            'password1': 'swordfish12',
            'password2': 'swordfish12',
            }

    def test_ReservedNameValidator(self):
        validator = validators.ReservedNameValidator()
        # has to raise ValidationError for each value
        for v in self.reserved_names:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v)
        # with value.lower()
        for v in self.reserved_names:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v.lower())
        # not a string type
        self.assertIs(None, validator(1))

    def test_validate_confusables(self):
        validator = validators.validate_confusables
        # has to raise ValidationError for each value
        for v in self.consfusables:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v)
        # with value.lower()
        for v in self.consfusables:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v.lower())
        # not a string type
        self.assertIs(None, validator(1))

    def test_validate_confusables_email(self):
        validator = validators.validate_confusables_email
        for v in self.consfusables_emails:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v)
        # with lower value
        for v in self.consfusables_emails:
            with self.subTest(value=v):
                with self.assertRaises(forms.ValidationError):
                    validator(v.lower())
        # @ not in value
        self.assertIs(None, validator('test'))