from django.contrib.auth import get_user_model, get_user
from django.test import override_settings
from hypothesis.extra.django import TestCase
from hypothesis import settings
from django.contrib.auth.base_user import AbstractBaseUser
from ..models import AbstractSuperUser
from django import db
from . import factories as ft
from ..managers import UserManager
import datetime
from django.contrib.auth import authenticate

ADMIN_URL = '/admin/'
hypothesis_default_settings = settings(max_examples=10)


# TODO LOOK WRITE AND REFACTOR
class UserModelAdminTestCase(TestCase):
    """
    TestS related to admin application in django.
    We want to make sure that normal user cannot
    be logged in into Admin and superuser can.
    """
    UserModel = get_user_model()
    ADMIN_URL = ADMIN_URL

    ##############################################
    # ------------------ASSERTS----------------- #
    #############################################

    def assertIsNotLoggedIntoAdmin(self, client):
        resp = client.get(self.ADMIN_URL)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.url)

    def assertIsLoggedIntoAdmin(self, client):
        resp = client.get(self.ADMIN_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('/login', resp.url)

    ##############################################
    # ------------------HELPERS----------------- #
    #############################################

    def create_normal_user(self, **kwargs):
        """
        Creates normal user.
        """
        return self.UserModel.objects.create_user(
            **kwargs
        )

    def create_superuser(self, **kwargs):
        """
        Creates normal user.
        """
        return self.UserModel.objects.create_superuser(
            **kwargs
        )

    ##############################################
    # ------------------TESTS------------------ #
    #############################################

    def test_admin_page_works(self):
        """
        Admin page answers with 302 and redirects to login.
        """
        resp = self.client.get(self.ADMIN_URL)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.url)

    @hypothesis_default_settings
    @ft.given_email
    def test_anonymous_user_is_not_logged_into_admin(self, email):
        """
        Create random user and check if
        we are logged into admin.
        """
        self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNotLoggedIntoAdmin(self.client)

    @hypothesis_default_settings
    @ft.given_email
    def test_active_user_is_not_logged_into_admin(self, email):
        """
        Create active user, log him in.
        We cant be logged into admin.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.client.login(
            username=email,
            password=ft.DEFAULT_PASSWORD,
        )
        auth_user = get
        self.assertIsNotLoggedIntoAdmin(self.client)