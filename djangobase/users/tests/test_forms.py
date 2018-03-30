from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm, UserAuthenticationForm

UserModel = get_user_model()


class UserRegistrationFormTestCase(TestCase):
    def setUp(self):
        self.form = UserRegistrationForm
        self.valid_form_data = dict(
            email='TestsdX@o2.pl',
            password1='password12',
            password2='password12',
        )

    def test_form_valid_data(self):
        form = UserRegistrationForm(self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_form_no_email(self):
        del self.valid_form_data['email']
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_form_no_password1(self):
        del self.valid_form_data['password1']
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_form_no_password2(self):
        del self.valid_form_data['password2']
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_form_short_password(self):
        self.valid_form_data['password1'] = '123123'
        self.valid_form_data['password2'] = '123123'
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_form_password_missmatch(self):
        self.valid_form_data['password1'] = '1123123AWSDl.3'
        self.valid_form_data['password2'] = '23.asD:DASlas93'
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_form_duplicate_user(self):
        # create good form
        form = UserRegistrationForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=True)
        # user should be inactive
        self.assertFalse(user.is_active)
        # we can't create user with same email address
        form = UserRegistrationForm(self.valid_form_data)
        self.assertFalse(form.is_valid())


class AuthenticationFormTestCase(TestCase):
    """
    Try to authenticate:
    1. active user
    2. inactive user
    3. non existent user
    """

    def create_user(self, active):
        user = UserModel.objects.create_user(**self.user_dict)
        user.is_active = active
        user.save()
        return user

    def setUp(self):
        self.user_dict = dict(
            email='TestQEmail@o2.pl',
            password='password12a'
        )

    def test_login_active_user(self):
        self.create_user(active=True)
        form = UserAuthenticationForm(data=self.user_dict)
        self.assertTrue(form.is_valid())

    def test_login_inactive_user(self):
        self.create_user(active=False)
        form = UserAuthenticationForm(data=self.user_dict)
        self.assertFalse(form.is_valid())

    def test_login_non_existent_user(self):
        form = UserAuthenticationForm(data=self.user_dict)
        self.assertFalse(form.is_valid())
