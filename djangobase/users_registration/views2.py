# -*- coding: utf-8 -*-
from braces.views import AnonymousRequiredMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import FormView, TemplateView
from django.contrib.auth.forms import PasswordResetForm
from users.forms import UserRegistrationForm

UserModel = get_user_model()

REGISTRATION_SECRET_KEY = 'secret_key'
REGISTRATION_EXPIRES_AFTER = 10
REGISTRATION_FROM_EMAIL = ''


class SendEmailMixin:
    email_subject_template = ''
    email_body_template = ''

    def get_email_subject(self, context):
        return render_to_string(self.email_subject_template, context)

    def get_email_message(self, context):
        return render_to_string(self.email_body_template, context)

    def send_email(self, from_email, to_email, context, **kwargs):
        message = self.get_email_message(context)
        subject = self.get_email_subject(context)
        # single line to avoid header-injection issues
        subject = ''.join(subject.splitlines())
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            **kwargs
        )


class UserRegistrationView(SendEmailMixin, FormView):
    template_name = 'registration/user_registration_view.html'

    success_url = 'user_registration_success_view'
    disallowed_url = 'user_registration_closed_view'

    form_class = UserRegistrationForm

    @staticmethod
    def registration_allowed():
        return getattr(settings, 'REGISTRATION_OPEN', False)

    def dispatch(self, request, *args, **kwargs):
        if self.registration_allowed() is False:
            return redirect(self.disallowed_url)
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_activation_key(user):
        return signing.dumps(
            obj=user.USERNAME_FIELD,
            salt=REGISTRATION_SECRET_KEY,
        )

    def get_email_context(self, activation_key):
        return {
            'activation_key': activation_key,
            'site': get_current_site(self.request),
            'scheme': self.request.scheme,
        }

    def form_valid(self, form):
        # create inactive user
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()
        # generate key and send email
        activation_key = self.get_activation_key(new_user)
        context = self.get_email_context(activation_key)
        self.send_email(
            to_email=new_user.email,
            from_email=REGISTRATION_FROM_EMAIL,
            context=context,
        )
        return redirect(self.success_url)


class UserActivationView(AnonymousRequiredMixin, TemplateView):
    """
    This template will be shown to user if activation fails
    (either activation key is invalid or expired).
    If activation is successful user will be redirected to success_url.
    """
    template_name = 'registration/user_activation_view.html'
    success_url = 'user_activation_success_view'
    activator = UserRegistrationActivator

    def get(self, *args, **kwargs):
        username = self.validate_activation_key(kwargs.get('activation_key'))
        if username:
            user = self.get(username)
            if user:
                user.is_active = True
                user.save()
                return redirect(self.success_url)
        return super(UserActivationView, self).get(*args, **kwargs)

    @staticmethod
    def validate_activation_key(key):
        try:
            value = signing.loads(
                s=key,
                salt=REGISTRATION_SECRET_KEY,
                max_age=REGISTRATION_EXPIRES_AFTER,
            )
            return value
        # SignatureExpired is a subclass of BadSignature,
        # so this will catch either one.
        except signing.BadSignature:
            return None

    @staticmethod
    def get_user(username):
        """
        Given validated email lookup and return
        corresponding user account if it exists
        or 'None' if it doesn't.
        """
        try:
            user = UserModel.objects.get(**{
                UserModel.USERNAME_FIELD: username,
                'is_active': False,
            })
            return user
        except UserModel.DoesNotExist:
            return None
