from django.contrib.auth import authenticate, get_user
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from faker.factory import Factory

from .settings import USER_REGISTRATION_SETTINGS

factory = Factory.create()
from django.core import mail


UserModel = get_user_model()


def get_random_post_data(*args, **kwargs):
    """
    generates data used to register a new user
    """
    password = factory.password()
    return dict(
        email=factory.email(),
        password1=password,
        password2=password,
    )


@override_settings(**USER_REGISTRATION_SETTINGS)
class UserRegistrationTestCase(TestCase):
    UserModel = get_user_model()

    def setUp(self):
        self.post_data = get_random_post_data()

    @override_settings(REGISTRATION_OPEN=False)
    def test_registration_closed(self):
        resp = self.client.get(reverse('user_registration_view'))
        self.assertRedirects(resp, reverse('user_registration_closed_view'))

    @override_settings(REGISTRATION_OPEN=True)
    def test_registration_open(self):
        resp = self.client.get(reverse('user_registration_view'))
        self.assertEqual(resp.status_code, 200)

    def test_register_random_users(self):
        # register given random user data
        for i in range(10):
            # clear outbox
            mail.outbox = []
            post_data = get_random_post_data()
            with self.subTest(data=post_data):
                resp = self.client.post(
                    reverse('user_registration_view'),
                    data=post_data
                )
                # check if registration was successful, we should be redirected
                self.assertRedirects(resp, reverse('user_registration_success_view'))
                # check if inbox has email
                self.assertGreater(len(mail.outbox), 0)
                self.assertEqual(mail.outbox[0].to, [post_data['email']])
                self.assertIn(resp.context['activation_key'], mail.outbox[0].body)

    def test_registration_fails_with_no_password(self):
        del self.post_data['password1']
        resp = self.client.post(
            reverse('user_registration_view'),
            data=self.post_data
        )
        self.assertEqual(resp.status_code, 200)

    def test_registration_fails_with_missmatch_passwords(self):
        self.post_data['password1'] = '11111111111111123as.das0d98asd0'
        resp = self.client.post(
            reverse('user_registration_view'),
            data=self.post_data
        )
        self.assertEqual(resp.status_code, 200)

    def test_register_user_and_activate(self):
        """
        Test whole registration workflow.
        """
        resp = self.client.post(
            reverse('user_registration_view'),
            data=self.post_data,
        )
        self.assertRedirects(resp, reverse('user_registration_success_view'))

        # check if user is created and inactive
        user = UserModel.objects.get(
            email=self.post_data['email'],
        )
        self.assertFalse(user.is_active)
        self.assertTrue(user.has_usable_password())

        # grab email
        email = mail.outbox[0]

        self.assertEqual(email.to, [self.post_data['email']])
        self.assertIsNotNone(email.from_email)
        self.assertIsNotNone(email.body)
        self.assertIsNotNone(email.subject)

        # grab activation_key from response context
        activation_key = resp.context['activation_key']

        self.assertIn(activation_key, email.body)

        # check if user cannot login (is_active should be false)
        authenticated_user = authenticate(
            username=self.post_data['email'],
            password=self.post_data['password1'],
        )
        self.assertIsNone(authenticated_user)

        # activate account
        resp = self.client.get(
            reverse(
                'user_activation_view',
                kwargs={'activation_key': activation_key}
            ))
        self.assertRedirects(resp, reverse('user_activation_success_view'))

        # verify that new user is activated
        user = UserModel.objects.get(email=self.post_data['email'])

        self.assertTrue(user.is_active)

        # authenticate new user
        authenticated_user = authenticate(
            username=self.post_data['email'],
            password=self.post_data['password1'],
        )
        self.assertEqual(authenticated_user, user)

        # check if sessions works for new user
        self.client.login(
            username=self.post_data['email'],
            password=self.post_data['password1'],
        )
        authenticated_user = get_user(self.client)
        self.assertEqual(authenticated_user, user)

        # logout user
        self.client.logout()

        # check if we cant register user with same data
        resp = self.client.post(
            reverse('user_registration_view'),
            data=self.post_data,
        )
        self.assertEqual(resp.status_code, 200)

    # TODO write whole workflow using sentry for email sending
    # or use selenium, and login to gmail inbox?


class UserActivationViewTestCase(TestCase):

    def test_activation_redirects_on_bad_activation_key(self):
        resp = self.client.get(
            reverse(
                'user_activation_view',
                kwargs={'activation_key': 'badactivationkey'}),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'registration/user_activation_view.html')

    # TODO write test that will delete user after registration and perform activation using valid activation_key
