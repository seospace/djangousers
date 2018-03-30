from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import FormView, TemplateView
from users.forms import UserRegistrationForm, UserPasswordResetForm
from django.conf import settings
from braces.views import AnonymousRequiredMixin
from django.urls import reverse
from activators.email import UserRegistrationActivator
from django.shortcuts import redirect

UserModel = get_user_model()


class UserRegistrationClosedView(AnonymousRequiredMixin, TemplateView):
    """
    Redirects here if REGISTRATION_OPEN = False in settings.py
    """
    template_name = 'registration/user_registration_closed_view.html'


class UserRegistrationSuccessView(AnonymousRequiredMixin, TemplateView):
    """
    Redirects here after user registers and activation_email is sent to him.
    """
    template_name = 'registration/user_registration_success_view.html'


class UserRegistrationView(AnonymousRequiredMixin, FormView):
    """
    Show registration form to user, send activation_key
    to user so he can activate his account.
    """
    template_name = 'registration/user_registration_view.html'
    disallowed_url = 'user_registration_closed_view'
    success_url = 'user_registration_success_view'

    form_class = UserRegistrationForm
    activator = UserRegistrationActivator

    @staticmethod
    def registration_allowed():
        return getattr(settings, 'REGISTRATION_OPEN', False)

    def dispatch(self, request, *args, **kwargs):
        if self.registration_allowed() is False:
            return redirect(self.disallowed_url)
        return super(UserRegistrationView, self).dispatch(request, *args, **kwargs)

    def send_activation_email(self, user):
        activator = self.activator(
            user=user,
            request=self.request,
        )
        activator.send_activation_email()

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()
        self.send_activation_email(new_user)
        return redirect(self.success_url)


class UserActivationSuccessView(AnonymousRequiredMixin, TemplateView):
    template_name = 'registration/user_activation_success_view.html'


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
        activated_user = self.activate_user(kwargs.get('activation_key'))
        if activated_user:
            return redirect(self.success_url)
        return super(UserActivationView, self).get(*args, **kwargs)

    def validate_activation_key(self, key):
        activator = self.activator()
        return activator.validate_key(key)

    def activate_user(self, key):
        user_email = self.validate_activation_key(key)
        if user_email:
            user = self.get_user(user_email)
            if user:
                user.is_active = True
                user.save()
                return user
        return None

    @staticmethod
    def get_user(email):
        """
        Given validated email lookup and return
        corresponding user account if it exists
        or 'None' if it doesn't.
        """
        try:
            user = UserModel.objects.get(
                email=email,
                is_active=False
            )
            return user
        except UserModel.DoesNotExist:
            return None


class UserPasswordRecoverySuccessView(AnonymousRequiredMixin, FormView):
    """
    User is redirected here after submitting email for password recovery.
    """
    template_name = 'recovery/user_password_recovery_success_view.html'


class UserPasswordRecoveryView(AnonymousRequiredMixin, FormView):
    """
    User can recover his lost password here.
    """
    form_class = UserPasswordResetForm
    success_url = 'user_password_recovery_success_view'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if email:
            user = self.get_user(email)
            if user:
                # send activation
                pass
        return redirect(reverse(self.success_url))

    @staticmethod
    def get_user(email):
        """
        Given validated email lookup and return
        corresponding user account if it exists
        or 'None' if it doesn't.
        """
        try:
            user = UserModel.objects.get(
                email=email,
                is_active=True,
            )
            return user
        except UserModel.DoesNotExist:
            return None