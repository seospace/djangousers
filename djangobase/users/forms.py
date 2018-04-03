# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import gettext_lazy as _
from .managers import BaseUserManager
from . import validators
from django.contrib.auth.forms import PasswordResetForm
UserModel = get_user_model()


class UserPasswordResetForm(forms.Form):
    email = forms.EmailField(
        required=True,
        validators=[validators.validate_confusables_email],
    )


class RegistrationForm(UserCreationForm):
    default_error_messages = {
        'reserved_name': 'To imie nie może zostac uzyte.',
        'confusable_value': 'Ta wartosc nie moza zostac uzyta.',
        'confusable_email': 'Ten email nie moze zostac uzyty.'
    }

    email = forms.EmailField(
        required=True,
        validators=[validators.validate_confusables_email]
    )

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ['email', 'password1', 'password2']


class AuthenticationForm(forms.Form):
    error_messages = {
        'invalid_login': _("Please enter a correct %(email)s and password. Note that both "
                           "fields may be case-sensitive.")
    }

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
        return self.cleaned_data
