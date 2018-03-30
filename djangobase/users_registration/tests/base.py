from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse
from django.test import Client


class TemplateResponseTestMixin:
    """
    Basic test checking if correct response, template,
    form, is rendered for the given view.
    Can be used for any CBV that inherits from TemplateResponseMixin.
    """
    view_class = None
    url_name = None
    url_name_kwargs = {}

    # optional (all below)
    template_name = None

    form_class = None
    csrf_token = None

    get_status_code = None
    post_status_code = None

    # if user that is authenticated should be redirected to other url
    # this should be a pattern name from urls.py
    authenticated_redirect_url_name = None

    def setUp(self):
        # client that is performing all requests
        # it should be set default by django testcase
        self.client = Client()
        # data used to create new active user
        self.user_data = {auth.get_user_model().USERNAME_FIELD: 'testowy@o2.pl', 'password': '1023909s0dc'}

    #############
    # SHORTCUTS #
    #############

    def get_response(self):
        """ returns response for given view """
        return self.client.get(reverse(self.url_name, kwargs=self.url_name_kwargs))

    def authenticate_client(self):
        """ this method should authenticate self.client """
        # login user
        self.client.login(**self.user_data)
        # check if user is authenticated
        user = auth.get_user(self.client)
        self.assertNotIsInstance(user, AnonymousUser, msg='User is not authenticated...')

    def create_active_user(self):
        """ create and return active user model instance """
        user = auth.get_user_model().objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        return user

    #########
    # TESTS #
    #########
    def test_view_used(self):
        """ check if correct view is used to render response """
        if self.view_class is None:
            self.skipTest('view_class attribute is None')
        resp = self.get_response()
        self.assertIsInstance(resp.context['view'], self.view_class)

    def test_template_used(self):
        """ check if correct template is used to render response """
        if self.template_name is None:
            self.skipTest('template_name attribute is None')
        resp = self.get_response()
        self.assertTemplateUsed(resp, self.template_name)

    def test_form_used(self):
        """ check if correct form is used to render response """
        if self.form_class is None:
            self.skipTest('form_class attribute is None')
        resp = self.get_response()
        self.assertIsInstance(resp.context['form'], self.form_class)

    def test_if_csrf_token_is_used(self):
        """ check if csrf_token is used to render response """
        if self.csrf_token is None:
            self.skipTest('csrf_token attribute is None')
        resp = self.get_response()
        self.assertIn('csrf_token', resp.context)

    def test_get_response(self):
        """ check if we receive correct status_code for GET request """
        if self.get_status_code is None:
            self.skipTest('get_status_code attribute is None')
        resp = self.get_response()
        self.assertEqual(resp.status_code, self.get_status_code)

    def test_post_response(self):
        """ check if we receive correct status_code for POST request """
        if self.post_status_code is None:
            self.skipTest('post_status_code attribute is None')
        resp = self.client.post(reverse(self.url_name, kwargs=self.url_name_kwargs), data={})
        self.assertEqual(resp.status_code, self.post_status_code)

    def test_authenticated_redirect(self):
        """ test if authenticated user is redirected to url """
        if self.authenticated_redirect_url_name is None:
            self.skipTest('authenticated_redirect_url_name attribute is None')
        # create active user
        self.create_active_user()
        # authenticate user
        self.authenticate_client()
        # finally process request
        resp = self.get_response()
        self.assertRedirects(resp, reverse(self.authenticated_redirect_url_name))