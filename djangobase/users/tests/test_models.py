import datetime
from collections import namedtuple

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, Client

User = get_user_model()
_MyUser = namedtuple('_MyUser', ['email', 'password'])


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = _MyUser('teSdsxowW@o2.pl', 'tajehaslo123')
        self.client = Client()
        self.admin_url = '/admin/'

    def test_User_attributes(self):
        """ test if User model has desired attributes """
        # we use email, always, period.
        self.assertTrue(hasattr(User, 'email'))
        self.assertEqual(User.USERNAME_FIELD, 'email')
        self.assertEqual(User.EMAIL_FIELD, 'email')
        # we use these fields, always, period.
        self.assertTrue(hasattr(User, 'is_active'))
        self.assertTrue(hasattr(User, 'is_staff'))
        self.assertTrue(hasattr(User, 'date_joined'))

    def test_create_user_good(self):
        # normal user was created
        user = User.objects.create_user(**self.user._asdict())
        # this user should not be active
        # before he verifies e-mail address
        self.assertIs(user.is_active, False)
        # this user should not be privileged
        self.assertIs(user.is_staff, False)
        # he joined...
        self.assertIsInstance(user.date_joined, datetime.datetime)
        # email has to match, lowercase
        self.assertEqual(user.email, self.user.email)
        # password has to be hashed
        self.assertNotEquals(user.password, self.user.password)

    def test_create_user_bad(self):
        # user with empty e-mail can't be created
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password=None)

    def test_create_user_with_empty_password(self):
        # password should be auto-generated if not provided
        user = User.objects.create_user(email='email@email.com')
        self.assertIsNot(None, user.password)

    def test_create_superuser(self):
        # regular superuser
        user = User.objects.create_superuser(**self.user._asdict())
        # has to be privileged
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    def test_admin_login_works(self):
        """ test if django-admin page is accessible """
        # visit admin page
        response = self.client.get(self.admin_url)
        # we should be redirected to login page
        self.assertEqual(302, response.status_code)
        self.assertIn('/login', response.url)

    def test_superuser_admin_login(self):
        """ test if superuser can be logged into django-admin """
        # create superuser
        User.objects.create_superuser(**self.user._asdict())
        # authenticate superuser
        authenticated = self.client.login(username=self.user.email, password=self.user.password)
        # check if we authenticate
        self.assertIs(authenticated, True)
        # visit admin page
        response = self.client.get(self.admin_url)
        # we should get 200 OK
        self.assertEqual(200, response.status_code)

    def test_normal_user_admin_login(self):
        """ test if normal user is not logged into django-admin """
        # create active normal user
        User.objects.create_user(**self.user._asdict(), is_active=True)
        # authenticate user
        authenticated = self.client.login(username=self.user.email, password=self.user.password)
        # check if we authenticate
        self.assertIs(authenticated, True)
        # visit admin page
        response = self.client.get(self.admin_url)
        # we should be redirected to login page
        self.assertEqual(302, response.status_code)
        self.assertIn('/login', response.url)

    def test_normal_inactive_user_permissions(self):
        # create user
        user = User.objects.create_user(**self.user._asdict())
        # all permissions should be False
        self.assertFalse(user.has_perm('perm'))
        self.assertFalse(user.has_perm('perm', obj=User))
        self.assertFalse(user.has_module_perms('app_label'))

    def test_normal_active_user_permissions(self):
        # create user
        user = User.objects.create_user(**self.user._asdict(), is_active=True)
        # all permissions should be False
        self.assertFalse(user.has_perm('perm'))
        self.assertFalse(user.has_perm('perm', obj=User))
        self.assertFalse(user.has_perms('perm'))
        self.assertFalse(user.has_perms('perm', obj=User))
        self.assertFalse(user.has_module_perms('app_label'))

    def test_superuser_permissions(self):
        # create superuser
        user = User.objects.create_superuser(**self.user._asdict())
        # all permissions should be True
        self.assertTrue(user.has_perm('perm'))
        self.assertTrue(user.has_perm('perm', obj=User))
        self.assertTrue(user.has_perms('perm'))
        self.assertTrue(user.has_perms('perm', obj=User))
        self.assertTrue(user.has_module_perms('app_label'))

    def test_send_email_to_user(self):
        """ test if sending email to user works """
        # create user
        user = User.objects.create_user(**self.user._asdict())
        # define test email context
        subject = 'test_subject'
        message = 'test_message'
        from_email = 'test@o2.pl'
        # send email
        user.email_user(subject, message, from_email)
        # get our e-mail
        email = mail.outbox[0]
        # assert e-mail was sent
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.body, message)
        self.assertEqual(email.from_email, from_email)
        self.assertEqual(email.to, [user.email])
