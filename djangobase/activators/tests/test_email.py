from django.core import mail
from django.test import SimpleTestCase, override_settings, TestCase, Client
from django.contrib.auth import get_user_model
from .settings import TEMPLATES, USER_REGISTRATION_ACTIVATOR_SETTINGS
from django.test import RequestFactory
from .base import UserRegistrationActivatorTestClass
import time
UserModel = get_user_model()


def get_new_user(data, active):
    """
    Creates new user from :param data
    with status :param active.
    """
    user = UserModel.objects.create_user(**data)
    user.is_active = active
    user.save()
    user.refresh_from_db()
    return user


@override_settings(TEMPLATES=TEMPLATES, **USER_REGISTRATION_ACTIVATOR_SETTINGS)
class UserRegistrationActivatorTestCase(TestCase):

    def setUp(self):
        self.user_kwargs = dict(
            email='testoWy@email.com',
            password='zxc098asd90dd.'
        )
        self.user = get_new_user(
            self.user_kwargs,
            active=False
        )

        self.kwargs = dict(
            user=self.user,
            request=RequestFactory().get('/'),
        )
        self.instance = UserRegistrationActivatorTestClass(
            **self.kwargs
        )

    def test_instance_has_attr_request(self):
        instance = self.instance
        self.assertIsNotNone(instance.request)

    def test_instance_has_attributes_from_settings(self):
        instance = self.instance

        self.assertEqual(instance.max_age, USER_REGISTRATION_ACTIVATOR_SETTINGS['REGISTRATION_MAX_AGE'])
        self.assertEqual(instance.salt, USER_REGISTRATION_ACTIVATOR_SETTINGS['REGISTRATION_SECRET_KEY'])
        self.assertEqual(instance.from_email, USER_REGISTRATION_ACTIVATOR_SETTINGS['REGISTRATION_FROM_EMAIL'])

    def test_instance_has_attr_user_email_as_value_to_sign(self):
        instance = self.instance

        self.assertEqual(instance.value_to_sign, self.user.email)
        self.assertEqual(instance.value_to_sign, self.user_kwargs['email'])

    def test_instance_has_attr_user_email_as_value_to_email(self):
        instance = self.instance

        self.assertEqual(instance.to_email, self.user.email)
        self.assertEqual(instance.to_email, self.user_kwargs['email'])

    def test_instance_attributes_values_are_equal(self):
        instance = self.instance

        self.assertEqual(instance.value_to_sign, self.user.email)
        self.assertEqual(instance.to_email, self.user.email)

        self.assertEqual(instance.value_to_sign, self.kwargs['user'].email)
        self.assertEqual(instance.to_email, self.kwargs['user'].email)

    def test_email_context_is_dict(self):
        context = self.instance.get_email_context()
        self.assertIsInstance(context, dict)

    def test_email_context_has_protocol(self):
        context = self.instance.get_email_context()
        self.assertIsNotNone(context['protocol'])

    def test_email_context_has_site(self):
        context = self.instance.get_email_context()
        self.assertIsNotNone(context['site'])

    def test_email_context_accepts_kwargs(self):
        additional_kwargs = dict(a=1, b='c')
        context = self.instance.get_email_context(**additional_kwargs)
        for k, v in additional_kwargs.items():
            with self.subTest(key=k, value=v):
                self.assertIn(k, context.keys())
                self.assertIn(v, context.values())

    def test_email_context_kwargs_overrides_defaults(self):
        context = self.instance.get_email_context(
            **dict(activation_key='test')
        )
        self.assertEqual(
            context['activation_key'],
            'test'
        )

    def test_activation_key_is_in_email_context(self):
        context = self.instance.get_email_context()
        self.assertIn('activation_key', context.keys())

    def test_activation_key_in_email_context_can_be_validated(self):
        context = self.instance.get_email_context()
        activation_key = context['activation_key']
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])

    def test_email_subject_and_message_are_correctly_rendered(self):
        # our templates should contain something for this test to pass
        subject, message = self.instance.get_email_subject_and_message()
        self.assertIsNotNone(subject)
        self.assertIsNotNone(message)

    def test_email_subject_avoids_header_injection(self):
        self.instance.email_subject_template = 'email_activators/BaseEmailActivator_subject_header_injection.txt'
        subject, message = self.instance.get_email_subject_and_message()

        subject_split = ''.join(subject.splitlines())
        self.assertEqual(subject, subject_split)

    def test_email_message_contains_valid_activation_key(self):
        # our templates should contain only
        # {{activation_key}} for this test to pass
        subject, message = self.instance.get_email_subject_and_message()

        activation_key = subject
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])

        activation_key = message
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])

    def test_send_activation_email_is_sent(self):
        self.instance.send_activation_email()
        self.assertGreater(len(mail.outbox), 0)

    def test_sending_activation_email_contains_desired_data(self):
        # our templates should contain only
        # {{activation_key}} for this test to pass
        self.instance.send_activation_email()
        email = mail.outbox[0]

        self.assertIsNotNone(email.body)
        self.assertIsNotNone(email.subject)

        activation_key = email.subject
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])

        activation_key = email.body
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])

        self.assertEqual(email.to, [self.user_kwargs['email']])
        self.assertEqual(email.to, [self.kwargs['user'].email])
        self.assertEqual(email.from_email, USER_REGISTRATION_ACTIVATOR_SETTINGS['REGISTRATION_FROM_EMAIL'])

    def test_can_validate_activation_key_from_activation_view(self):
        """
        create new activator instance without User and Request.
        then validate key sent via email by first instance.
        """
        self.instance.send_activation_email()

        email = mail.outbox[0]
        activation_key = email.subject

        new_instance = UserRegistrationActivatorTestClass(
            user=None,
            request=None,
        )
        valid = new_instance.validate_key(activation_key)
        self.assertEqual(valid, self.user_kwargs['email'])
        self.assertEqual(valid, self.user.email)

    @override_settings(REGISTRATION_MAX_AGE=0.00000001)
    def test_activation_key_can_expire(self):
        instance = UserRegistrationActivatorTestClass(**self.kwargs)

        key = instance.generate_key('test@value.com')
        time.sleep(0.00000001)
        valid = instance.validate_key(key)
        self.assertIsNone(valid)
