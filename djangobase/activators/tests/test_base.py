import time

from django.core import mail
from django.test import SimpleTestCase, override_settings
from hypothesis import given, settings
from hypothesis import strategies as st

from .base import BaseEmailActivatorTestClass
from .settings import TEMPLATES
from ..base import BaseActivator


class BaseActivatorTestCase(SimpleTestCase):

    @given(salt=st.text(), value=st.text())
    @settings(max_examples=100)
    def test_generate_and_validate_with_random_text(self, salt, value):
        # create activator instance
        activator = BaseActivator(salt=salt, max_age=1000)
        # generate key
        key = activator.generate_key(value)
        # validate key
        valid = activator.validate_key(key)
        self.assertEqual(value, valid)

    @given(salt=st.text(), value=st.text())
    @settings(max_examples=100)
    def test_generate_and_validate_random_text_expired(self, salt, value):
        max_age = 0.00000001
        # create activator instance
        activator = BaseActivator(salt=salt, max_age=max_age)
        # generate key
        key = activator.generate_key(value)
        # sleep for some time
        time.sleep(max_age + max_age)
        # validate key
        valid = activator.validate_key(key)
        self.assertIsNone(valid)


@override_settings(TEMPLATES=TEMPLATES)
class BaseEmailActivatorTestCase(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        cls.class_init_kwargs = dict(
            value_to_sign='test_value',
            from_email='from@email.com',
            to_email='to@email.com',
            salt='secret',
            max_age=80000,
        )
        super(BaseEmailActivatorTestCase, cls).setUpClass()

    def setUp(self):
        self.kwargs = self.class_init_kwargs.copy()
        self.instance = BaseEmailActivatorTestClass(**self.kwargs)
        mail.outbox = []

    def test_instance_has_attributes(self):
        for key in self.kwargs:
            with self.subTest(attr=key):
                self.assertTrue(
                    hasattr(self.instance, key)
                )

    def test_instance_getattr_are_equal(self):
        for key, value in self.kwargs.items():
            with self.subTest(attr_key=key, value=value):
                self.assertEqual(
                    getattr(self.instance, key),
                    value,
                )

    def test_email_context_is_dict(self):
        context = self.instance.get_email_context()
        self.assertIsInstance(context, dict)

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
        self.assertEqual(valid, self.kwargs['value_to_sign'])

    def test_email_subject_and_message_are_correctly_rendered(self):
        # our templates should contain something for this test to pass
        subject, message = self.instance.get_email_subject_and_message()
        self.assertIsNotNone(subject)
        self.assertIsNotNone(message)

    def test_email_subject_avoid_header_injection(self):
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
        self.assertEqual(valid, self.kwargs['value_to_sign'])

        activation_key = message
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.kwargs['value_to_sign'])

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
        self.assertEqual(valid, self.kwargs['value_to_sign'])

        activation_key = email.body
        valid = self.instance.validate_key(activation_key)
        self.assertEqual(valid, self.kwargs['value_to_sign'])

        self.assertEqual(email.to, [self.kwargs['to_email']])
        self.assertEqual(email.from_email, self.kwargs['from_email'])

    def test_activation_key_can_expire(self):
        self.kwargs['max_age'] = 0.00000001
        self.instance = BaseEmailActivatorTestClass(**self.kwargs)

        instance = self.instance
        key = instance.generate_key(self.kwargs['value_to_sign'])
        time.sleep(self.kwargs['max_age'] + 0.00000001)
        valid = instance.validate_key(key)
        self.assertIsNone(valid)
