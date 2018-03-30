from django.test import TestCase

from .base import TemplateResponseTestMixin
from users.forms import UserRegistrationForm, UserAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from .. import views
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse
from users.forms import UserRegistrationForm
_auth_redirect = 'index'


class UserRegistrationClosedViewTestCase(TemplateResponseTestMixin, TestCase):
    view_class = views.UserRegistrationClosedView
    url_name = 'user_registration_closed_view'
    template_name = 'registration/user_registration_closed_view.html'

    get_status_code = 200
    post_status_code = 405

    authenticated_redirect_url_name = _auth_redirect


class UserRegistrationSuccessViewTestCase(TemplateResponseTestMixin, TestCase):
    view_class = views.UserRegistrationSuccessView
    url_name = 'user_registration_success_view'
    template_name = 'registration/user_registration_success_view.html'

    get_status_code = 200
    post_status_code = 405

    authenticated_redirect_url_name = _auth_redirect


class UserRegistrationViewTestCase(TemplateResponseTestMixin, TestCase):
    view_class = views.UserRegistrationView
    url_name = 'user_registration_view'
    template_name = 'registration/user_registration_view.html'
    form_class = UserRegistrationForm

    csrf_token = True
    get_status_code = 200
    post_status_code = 200

    authenticated_redirect_url_name = _auth_redirect


class UserActivationSuccessViewTestCase(TemplateResponseTestMixin, TestCase):
    view_class = views.UserActivationSuccessView
    url_name = 'user_activation_success_view'
    template_name = 'registration/user_activation_success_view.html'

    get_status_code = 200
    post_status_code = 405

    authenticated_redirect_url_name = _auth_redirect


class UserActivationViewTestCase(TemplateResponseTestMixin, TestCase):
    view_class = views.UserActivationView
    url_name = 'user_activation_view'
    url_name_kwargs = {'activation_key': 'someactivationkey'}
    template_name = 'registration/user_activation_view.html'

    get_status_code = 200
    post_status_code = 405

    authenticated_redirect_url_name = _auth_redirect
