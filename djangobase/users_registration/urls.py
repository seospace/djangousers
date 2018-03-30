from django.urls import path
from .views import (
    UserRegistrationClosedView,
    UserRegistrationSuccessView,
    UserRegistrationView,
    UserActivationView,
    UserActivationSuccessView,
)

urlpatterns = [
    path('rejestracja/sukces', UserRegistrationSuccessView.as_view(), name='user_registration_success_view'),
    path('rejestracja/zamknieta/', UserRegistrationClosedView.as_view(), name='user_registration_closed_view'),
    path('rejestracja/', UserRegistrationView.as_view(), name='user_registration_view'),
    path('aktywacja/sukces', UserActivationSuccessView.as_view(), name='user_activation_success_view'),
    path('aktywacja/<activation_key>', UserActivationView.as_view(), name='user_activation_view'),
]
