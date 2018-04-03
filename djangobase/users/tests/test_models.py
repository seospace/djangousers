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
UserModel = get_user_model()
hypothesis_default_settings = settings(max_examples=10)


@override_settings(AUTHENTICATION_BACKENDS=['users.auth.EmailBackend'])
class UserModelTestCase(TestCase):
    """
    Create normal users and superusers.
    Make sure they have correct attributes:
    superusers should be superusers, staff and active,
    normal users cannot be superuser or staff.
    Their permissions should match too, superuser has all
    permissions while normal user has zero permissions.
    """
    UserModel = get_user_model()

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

    ##############################################
    # ------------------TESTS----------------- #
    #############################################

    def test_model_has_correct_manager(self):
        self.assertIsInstance(
            self.UserModel.objects,
            UserManager,
        )

    def test_model_has_email_attribute(self):
        self.assertTrue(
            hasattr(self.UserModel, 'email')
        )

    def test_model_USERNAME_FIELD_equals_email(self):
        self.assertEqual(
            getattr(self.UserModel, 'USERNAME_FIELD'),
            'email',
        )

    def test_model_EMAIL_FIELD_equals_email(self):
        self.assertEqual(
            getattr(self.UserModel, 'USERNAME_FIELD'),
            'email',
        )

    def test_model_has_date_joined_attribute(self):
        self.assertTrue(
            hasattr(self.UserModel, 'date_joined')
        )

    def test_model_has_is_active_attribute(self):
        self.assertTrue(
            hasattr(self.UserModel, 'is_active')
        )

    def test_model_has_is_staff_attribute(self):
        self.assertTrue(
            hasattr(self.UserModel, 'is_staff')
        )

    def test_model_has_is_superuser_attribute(self):
        self.assertTrue(
            hasattr(self.UserModel, 'is_superuser')
        )

    @hypothesis_default_settings
    @ft.given_email
    def test_model_creates_user(self, email):
        """
        Model can create an user instance.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNotNone(user)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_is_inactive(self, email):
        """
        By default user is not active.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_active)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_is_not_staff(self, email):
        """
        By default user is not a staff member.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_staff)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_is_not_superuser(self, email):
        """
        By default user is not superuser.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_superuser)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_has_hashed_password(self, email):
        """
        Password is not stored raw.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsNot(
            user.password,
            ft.DEFAULT_PASSWORD
        )

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_has_date_joined(self, email):
        """
        He joined somewhere in time, did he ?
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertIsInstance(
            user.date_joined,
            datetime.datetime,
        )

    @hypothesis_default_settings
    @ft.given_email
    def test_created_inactive_user_has_no_permissions(self, email):
        """
        User should be non-privileged.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertFalse(user.is_active)

        self.assertFalse(user.has_perm())
        self.assertFalse(user.has_perm('perm'))

        self.assertFalse(user.has_perms())
        self.assertFalse(user.has_perms('perm'))

        self.assertFalse(user.has_module_perms())
        self.assertFalse(user.has_module_perms('perm'))

    @hypothesis_default_settings
    @ft.given_email
    def test_created_active_user_has_no_permissions(self, email):
        """
        User should be non-privileged.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
            is_active=True,
        )
        self.assertTrue(user.is_active)

        self.assertFalse(user.has_perm())
        self.assertFalse(user.has_perm('perm'))

        self.assertFalse(user.has_perms())
        self.assertFalse(user.has_perms('perm'))

        self.assertFalse(user.has_module_perms())
        self.assertFalse(user.has_module_perms('perm'))

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_can_check_password(self, email):
        """
        Created user can validate his password.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        self.assertTrue(
            user.check_password(ft.DEFAULT_PASSWORD)
        )

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_cannot_be_duplicate(self, email):
        """
        Cannot create user with existing email value.
        """
        self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        with self.assertRaises(db.IntegrityError):
            self.create_normal_user(
                email=email,
                password=ft.DEFAULT_PASSWORD,
            )

    @hypothesis_default_settings
    @ft.given_email
    def test_created_user_can_change_password_and_validate_it(self, email):
        """
        User can change password and validate
        password with new value.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )
        user.set_password('new_password')
        user.save()

        valid = user.check_password(ft.DEFAULT_PASSWORD)
        self.assertFalse(valid)

        valid = user.check_password('new_password')
        self.assertTrue(valid)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_inactive_user_cannot_authenticate_with_EmailBackend(self, email):
        """
        Test if created user cannot authenticate.
        By default is_active = False for the user.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
        )

        auth_user = authenticate(
            email=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(auth_user)

        auth_user = authenticate(
            username=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(auth_user)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_active_user_can_authenticate_with_EmailBackend(self, email):
        """
        Test if created user can authenticate.
        We set is_active flag to True for the user.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
            is_active=True,
        )

        auth_user = authenticate(
            email=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertEqual(user, auth_user)

        auth_user = authenticate(
            username=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertEqual(user, auth_user)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_active_user_cannot_authenticate_with_EmailBackend_after_changing_password(self, email):
        """
        After changing password user
        cannot authenticate providing old password.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
            is_active=True,
        )
        # set new password for user
        user.set_password('09098dsf9')
        user.save()

        auth_user = authenticate(
            email=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(auth_user)

        auth_user = authenticate(
            username=email,
            password=ft.DEFAULT_PASSWORD
        )
        self.assertIsNone(auth_user)

    @hypothesis_default_settings
    @ft.given_email
    def test_created_active_user_can_authenticate_with_EmailBackend_after_changing_password(self, email):
        """
        After changing password user
        can authenticate providing new password.
        """
        user = self.create_normal_user(
            email=email,
            password=ft.DEFAULT_PASSWORD,
            is_active=True,
        )
        # set new password for user
        user.set_password('09098dsf9')
        user.save()

        auth_user = authenticate(
            email=email,
            password='09098dsf9'
        )
        self.assertEqual(user, auth_user)

        auth_user = authenticate(
            username=email,
            password='09098dsf9'
        )
        self.assertEqual(user, auth_user)


class UserModelAdminTestCase(TestCase):
    """
    Test related to admin application in django.
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
    #
    # def test_inactive_user_is_not_logged_into_admin(self):
    #     """
    #     User has no permissions to see admin...
    #     """
    # def test_admin_login_works(self):
    #     """ test if django-admin page is accessible """
    #     # visit admin page
    #     response = self.client.get(self.admin_url)
    #     # we should be redirected to login page
    #     self.assertEqual(302, response.status_code)
    #     self.assertIn('/login', response.url)
    #
    # def test_superuser_admin_login(self):
    #     """ test if superuser can be logged into django-admin """
    #     # create superuser
    #     User.objects.create_superuser(**self.user._asdict())
    #     # authenticate superuser
    #     authenticated = self.client.login(username=self.user.email, password=self.user.password)
    #     # check if we authenticate
    #     self.assertIs(authenticated, True)
    #     # visit admin page
    #     response = self.client.get(self.admin_url)
    #     # we should get 200 OK
    #     self.assertEqual(200, response.status_code)
    #
    # def test_normal_user_admin_login(self):
    #     """ test if normal user is not logged into django-admin """
    #     # create active normal user
    #     User.objects.create_user(**self.user._asdict(), is_active=True)
    #     # authenticate user
    #     authenticated = self.client.login(username=self.user.email, password=self.user.password)
    #     # check if we authenticate
    #     self.assertIs(authenticated, True)
    #     # visit admin page
    #     response = self.client.get(self.admin_url)
    #     # we should be redirected to login page
    #     self.assertEqual(302, response.status_code)
    #     self.assertIn('/login', response.url)

    #
    # ##############
    # # SUPERUSER #
    # ##############
    #
    # @ft.given_email
    # def test_can_create_superuser(self, email):
    #     """
    #     Test if our manager can create superuser.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #     )
    #     self.assertIsNotNone(user)
    #
    # @ft.given_email
    # def test_created_superuser_is_active(self, email):
    #     """
    #     Test if created superuser is inactive by default.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #     )
    #     self.assertTrue(user.is_active)
    #
    # @ft.given_email
    # def test_created_superuser_is_staff(self, email):
    #     """
    #     Test if created superuser is a staff member.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #     )
    #     self.assertTrue(user.is_staff)
    #
    # @ft.given_email
    # def test_created_superuser_is_superuser(self, email):
    #     """
    #     Test if created superuser is superuser.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #     )
    #     self.assertTrue(user.is_superuser)
    #
    # @ft.given_email
    # def test_created_inactive_superuser_cannot_authenticate_with_EmailBackend(self, email):
    #     """
    #     Test if created superuser cannot authenticate.
    #     Beacuse we set is_active = False for the superuser.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #         is_active=False,
    #     )
    #
    #     auth_user = authenticate(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD
    #     )
    #     self.assertIsNone(auth_user)
    #
    #     auth_user = authenticate(
    #         username=email,
    #         password=ft.DEFAULT_PASSWORD
    #     )
    #     self.assertIsNone(auth_user)
    #
    # @ft.given_email
    # def test_created_default_superuser_can_authenticate_with_EmailBackend(self, email):
    #     """
    #     Test if created superuser can authenticate.
    #     """
    #     user = self.create_superuser(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD,
    #     )
    #
    #     auth_user = authenticate(
    #         email=email,
    #         password=ft.DEFAULT_PASSWORD
    #     )
    #     self.assertEqual(user, auth_user)
    #
    #     auth_user = authenticate(
    #         username=email,
    #         password=ft.DEFAULT_PASSWORD
    #     )
    #     self.assertEqual(user, auth_user)