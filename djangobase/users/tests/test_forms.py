from django.contrib.auth import authenticate
from django.test import override_settings
from hypothesis import (
    settings, reproduce_failure
)
from hypothesis.extra.django import TestCase
from . import factories as ft
from ..forms import RegistrationForm, AuthenticationForm
from .. import validators


@override_settings(
    AUTHENTICATION_BACKENDS=['users.auth.EmailBackend'],
    AUTH_PASSWORD_VALIDATORS=[]
)
class RegistrationFormTestCase(TestCase):

    def assertFormInvalid(self, post_data):
        """
        Checks if form is invalid
        with given post_data.
        """
        form = RegistrationForm(post_data)
        self.assertFalse(form.is_valid(), msg=(post_data, form.errors))
        # TODO add correct messages to assert errors

    def assertFormValid(self, post_data):
        """
        Checks if form is valid
        with given post_data.
        """
        form = RegistrationForm(post_data)
        self.assertTrue(form.is_valid(), msg=(post_data, form.errors))

    def get_user_from_data(self, post_data):
        """
        Checks if form is correct and returns
        user instance by calling form.save()
        """
        form = RegistrationForm(post_data)
        self.assertTrue(form.is_valid(), msg=(post_data, form.errors))
        user = form.save(commit=True)
        self.assertIsNotNone(user)
        return user

    #########
    # TESTS #
    #########

    def test_form_has_correct_fields(self):
        """
        Test if form has correct fields.
        """
        form = RegistrationForm()

        self.assertTrue('email' in form.fields,)
        self.assertTrue('password1' in form.fields,)
        self.assertTrue('password2' in form.fields,)

    def test_form_email_field_has_correct_validators(self):
        form = RegistrationForm()
        self.assertTrue(
            validators.validate_confusables_email in
            form.fields['email'].validators
        )

    @ft.given_user_registration_data
    def test_form_is_valid(self, post_data):
        """
        Form is valid given correct data.
        """
        self.assertFormValid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_without_email(self, post_data):
        """
        Form is invalid without email field.
        """
        del post_data['email']
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_without_password1(self, post_data):
        """
        Form is invalid without password1 field.
        """
        del post_data['password1']
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_without_password2(self, post_data):
        """
        Form is invalid without password2 field.
        """
        del post_data['password2']
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_with_passwords_missmatch(self, post_data):
        """
        Form is invalid if passwords missmatch.
        """
        post_data['password1'] = '3213321dxccx'
        post_data['password2'] = '123asdasd33s'
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_with_empty_password1(self, post_data):
        """
        Form is invalid without password1.
        """
        del post_data['password1']
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_is_invalid_with_empty_password2(self, post_data):
        """
        Form is invalid without password2.
        """
        del post_data['password2']
        self.assertFormInvalid(post_data)

    @ft.given_user_registration_data
    def test_form_creates_new_user(self, post_data):
        """
        Form can create new user with correct data.
        """
        self.get_user_from_data(post_data)

    @ft.given_user_registration_data
    def test_user_created_by_form_is_not_active(self, post_data):
        """
        User created by form should not be active.
        """
        user = self.get_user_from_data(post_data)
        self.assertFalse(user.is_active)

    @ft.given_user_registration_data
    def test_user_created_by_form_is_not_superuser(self, post_data):
        """
        User created by form should not be superuser.
        """
        user = self.get_user_from_data(post_data)
        self.assertFalse(user.is_superuser)

    @ft.given_user_registration_data
    def test_user_created_by_form_is_not_staff(self, post_data):
        """
        User created by form should not be superuser.
        """
        user = self.get_user_from_data(post_data)
        self.assertFalse(user.is_staff)

    @ft.given_user_registration_data
    def test_user_created_by_form_can_validate_password(self, post_data):
        """
        User created by form can validate password
        with the password given during filling form.
        """
        user = self.get_user_from_data(post_data)
        self.assertTrue(user.check_password(post_data['password1']))
        self.assertTrue(user.check_password(post_data['password2']))

    @ft.given_user_registration_data
    def test_user_created_by_form_has_given_email(self, post_data):
        """
        User created by form has email equal
        to given during filling form.
        """
        user = self.get_user_from_data(post_data)
        self.assertEqual(
            user.email,
            post_data['email'],
        )

    @ft.given_user_registration_data
    def test_form_creates_new_user_with_desired_attributes_values(self, post_data):
        """
        User created by form `save` method
        has desired values for certain attributes.
        """
        user = self.get_user_from_data(post_data)

        # emails should match
        self.assertEqual(user.email, post_data['email'])
        # password should match
        self.assertTrue(user.check_password(post_data['password1']))
        self.assertTrue(user.check_password(post_data['password2']))
        # user should not be: active, staff, superuser
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    @ft.given_user_registration_data
    def test_form_is_invalid_with_existing_email_in_database(self, post_data):
        """
        Form is invalid if save() was already
        called for the same data. It means user
        already exists with the given email.
        """
        # first form should be valid
        self.assertFormValid(post_data)
        # create user
        self.get_user_from_data(post_data)
        # form should be invalid
        self.assertFormInvalid(post_data)


@override_settings(
    AUTHENTICATION_BACKENDS=['users.auth.EmailBackend'],
    AUTH_PASSWORD_VALIDATORS=[]
)
class AuthenticationFormTestCase(TestCase):

    def assertFormInvalid(self, post_data):
        """
        Checks if form is invalid
        with given post_data.
        """
        form = AuthenticationForm(data=post_data)
        self.assertFalse(form.is_valid(), msg=(post_data, form.errors))
        # TODO add correct messages to assert errors

    def assertFormValid(self, post_data):
        """
        Checks if form is valid
        with given post_data.
        """
        form = AuthenticationForm(data=post_data)
        self.assertTrue(form.is_valid(), msg=(post_data, form.errors))
        # TODO make self.form

    #########
    # TESTS #
    #########

    def test_form_has_correct_fields(self):
        """
        Test if form has correct fields.
        """
        form = AuthenticationForm()

        self.assertTrue('email' in form.fields)
        self.assertTrue('password' in form.fields)

    @ft.given_active_user
    def test_form_is_valid_on_active_user(self, active_user):
        """
        Given active user, form is valid.
        """
        self.assertFormValid(
            dict(
                email=active_user.email,
                password=ft.DEFAULT_PASSWORD,
            )
        )

    @ft.given_inactive_user
    def test_form_is_invalid_on_inactive_user(self, inactive_user):
        """
        Given inactive user, form is invalid.
        """
        self.assertFormInvalid(
            dict(
                email=inactive_user.email,
                password=ft.DEFAULT_PASSWORD,
            )
        )

    @ft.given_email
    def test_form_is_invalid_on_nonexistent_user(self, email):
        """
        Given user that doesnt exist, form is invalid.
        """
        self.assertFormInvalid(
            dict(
                email=email,
                password=ft.DEFAULT_PASSWORD,
            )
        )

    @ft.given_active_user
    def test_form_is_invalid_on_user_password_change(self, active_user):
        """
        After changing user password form is invalid
        with old password given.
        """
        active_user.set_password('not_default_password12')
        active_user.save()

        self.assertFormInvalid(
            dict(
                email=active_user.email,
                password=ft.DEFAULT_PASSWORD,
            )
        )

    @ft.given_active_user
    def test_form_valid_on_user_password_change(self, active_user):
        """
        After changing user password form is valid
        with new password given.
        """
        active_user.set_password('not_default_password12')
        active_user.save()

        self.assertFormValid(
            dict(
                email=active_user.email,
                password='not_default_password12',
            )
        )
