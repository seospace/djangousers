# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import gettext_lazy as _
from django import forms
from . import validators

UserModel = get_user_model()


class UserPasswordResetForm(forms.Form):
    email = forms.EmailField(
        required=True,
        validators=validators.validate_confusables_email,
    )


class UserRegistrationForm(UserCreationForm):
    default_error_messages = {
        'reserved_name': 'To imie nie może zostac uzyte.',
        'confusable_value': 'Ta wartosc nie moza zostac uzyta.',
        'confusable_email': 'Ten email nie moze zostac uzyty.'
    }

    email = forms.EmailField(
        required=True,
        validators=[
            validators.validate_confusables_email
        ]
    )

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ['email', 'password1', 'password2']


class UserAuthenticationForm(forms.Form):
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

        # Set the label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': self.username_field.verbose_name},
                )
        return self.cleaned_data
    #
    # def confirm_login_allowed(self, user):
    #     """
    #     Controls whether the given User may log in. This is a policy setting,
    #     independent of end-user authentication. This default behavior is to
    #     allow login by active users, and reject login by inactive users.
    #
    #     If the given user cannot log in, this method should raise a
    #     ``forms.ValidationError``.
    #
    #     If the given user may log in, this method should return None.
    #     """
    #     if not user.is_active:
    #         raise forms.ValidationError(
    #             self.error_messages['inactive'],
    #             code='inactive',
    #         )
    #     return None
    #
    # def get_user_id(self):
    #     if self.user_cache:
    #         return self.user_cache.id
    #     return None
    #
    # def get_user(self):
    #     return self.user_cache
