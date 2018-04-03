from django.contrib.auth import get_user_model
from django.test import override_settings
from hypothesis.extra.django import TestCase

from . import factories as ft
from ..managers import UserManager


class UserManagerTestCase(TestCase):
    UserModel = get_user_model()

    def create_normal_user(self, **kwargs):
        return self.UserModel.objects.create_user(
            **kwargs
        )

    def create_superuser(self, **kwargs):
        return self.UserModel.objects.create_superuser(
            **kwargs
        )

    def test_UserModel_has_correct_manager(self):
        """
        Before we do any tests, make sure
        that our UserModel manager is the manager
        that we actually want to test.
        """
        self.assertIsInstance(
            self.UserModel.objects,
            UserManager,
        )

    @ft.given_email
    def test_cannot_create_user_with_empty_email(self, email):
        """
        ValueError should be raised on missing email.
        """
        with self.assertRaises(ValueError):
            self.create_normal_user(
                email=None,
                password=ft.DEFAULT_PASSWORD,
            )

    @ft.given_email
    def test_can_create_user(self, email):
        """
        Test if our manager can create user.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNotNone(user)

    @ft.given_email
    def test_created_user_is_inactive(self, email):
        """
        Test if created user is inactive by default.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_active)

    @ft.given_email
    def test_created_user_is_not_staff(self, email):
        """
        Test if created user is not a staff member.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_staff)

    @ft.given_email
    def test_created_user_is_not_superuser(self, email):
        """
        Test if created user is not a superuser
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_superuser)

    ##############
    # SUPERUSER #
    ##############

    @ft.given_email
    def test_cannot_create_superuser_with_empty_email(self, email):
        """
        ValueError should be raised on missing email.
        """
        with self.assertRaises(ValueError):
            self.create_superuser(
                email=None,
                password=ft.DEFAULT_PASSWORD,
            )

    @ft.given_email
    def test_can_create_superuser(self, email):
        """
        Test if our manager can create superuser.
        """
        user = self.create_superuser(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNotNone(user)

    @ft.given_email
    def test_created_superuser_is_active(self, email):
        """
        Test if created superuser is inactive by default.
        """
        user = self.create_superuser(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertTrue(user.is_active)

    @ft.given_email
    def test_created_superuser_is_staff(self, email):
        """
        Test if created superuser is a staff member.
        """
        user = self.create_superuser(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertTrue(user.is_staff)

    @ft.given_email
    def test_created_superuser_is_superuser(self, email):
        """
        Test if created superuser is superuser.
        """
        user = self.create_superuser(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertTrue(user.is_superuser)
