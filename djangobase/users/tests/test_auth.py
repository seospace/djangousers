from django.contrib.auth import authenticate
from django.test import override_settings
from hypothesis import (
    settings
)
from hypothesis.extra.django import TestCase

from . import factories as ft


@override_settings(
    AUTHENTICATION_BACKENDS=['users.auth.EmailBackend'],
    AUTH_PASSWORD_VALIDATORS=[]
)
class EmailBackendTestCase(TestCase):

    @settings(max_examples=10)
    @ft.given_active_user
    def test_active_user_can_login_with_username_kwarg(self, active_user):
        valid = authenticate(
            username=active_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertEqual(active_user, valid)

    @settings(max_examples=10)
    @ft.given_inactive_user
    def test_inactive_user_cannot_login_with_username_kwarg(self, inactive_user):
        valid = authenticate(
            username=inactive_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(valid)

    @settings(max_examples=10)
    @ft.given_active_user
    def test_active_user_can_login_with_email_kwarg(self, active_user):
        valid = authenticate(
            email=active_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertEqual(active_user, valid)

    @settings(max_examples=10)
    @ft.given_inactive_user
    def test_inactive_user_cannot_login_with_email_kwarg(self, inactive_user):
        valid = authenticate(
            email=inactive_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(valid)

    @settings(max_examples=10)
    @ft.given_active_user
    def test_active_user_can_login_with_username_and_email_kwarg(self, active_user):
        valid = authenticate(
            username=active_user.email,
            email=active_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertEqual(active_user, valid)

    @settings(max_examples=10)
    @ft.given_inactive_user
    def test_inactive_user_cannot_login_with_username_and_email_kwarg(self, inactive_user):
        valid = authenticate(
            username=inactive_user.email,
            email=inactive_user.email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(valid)

    @settings(max_examples=10)
    @ft.given_active_user
    def test_active_user_can_login_with_username_and_email_kwarg_after_changing_password(self, active_user):
        active_user.set_password('new_password')
        active_user.save()

        valid = authenticate(
            username=active_user.email,
            email=active_user.email,
            password='new_password',
        )
        self.assertEqual(active_user, valid)

    @settings(max_examples=10)
    @ft.given_active_user
    def test_active_user_cannot_login_with_username_and_email_kwarg_after_changing_password(self, active_user):
        active_user.set_password('new_password')
        active_user.save()

        valid = authenticate(
            username=active_user.email,
            email=active_user.email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNone(valid)