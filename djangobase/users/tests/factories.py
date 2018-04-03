import string

from django.contrib.auth import get_user_model
from hypothesis import (
    given,
    strategies as st,
)

DEFAULT_PASSWORD = 'default_password'

UserModel = get_user_model()


def create_registration_post_data(email, password):
    return dict(
        email=email,
        password1=password,
        password2=password,
    )


def create_user(email, password, is_active):
    return UserModel.objects.create_user(email=email, password=password, is_active=is_active)


def build_email(hostname, domain):
    return hostname + '@' + domain + '.cOm'


given_user_registration_data = given(
    post_data=st.builds(
        create_registration_post_data,
        email=st.builds(
                build_email,
                hostname=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12),
                domain=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12)
            ),
        password=st.text(min_size=3, alphabet=string.ascii_letters),
    )
)

given_email = given(
    email=st.builds(
                build_email,
                hostname=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12),
                domain=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12)
            ),
)

given_active_user = given(
    active_user=st.builds(
        create_user,
        email=st.builds(
                build_email,
                hostname=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12),
                domain=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12)
            ),
        password=st.just(DEFAULT_PASSWORD),
        is_active=st.just(True),
    )
)

given_inactive_user = given(
    inactive_user=st.builds(
        create_user,
        email=st.builds(
                build_email,
                hostname=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12),
                domain=st.text(alphabet=string.ascii_letters + string.digits, min_size=12, max_size=12)
            ),
        password=st.just(DEFAULT_PASSWORD),
        is_active=st.just(False),
    )
)

#
# class UserFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = UserModel
#
#     email = factory.fuzzy.FuzzyAttribute(random_email)
#     password = factory.PostGenerationMethodCall('set_password', DEFAULT_PASSWORD)
#
#
# class RegistrationData(object):
#     def __init__(self, email, password):
#         self.email = email
#         self.password1 = password
#         self.password2 = password
#
#     def __str__(self):
#         return self.email, self.password1
#
#     @property
#     def as_dict(self):
#         return self.__dict__
#
#
# class RegistrationDataFactory(factory.Factory):
#     class Meta:
#         model = RegistrationData
#
#     email = factory.fuzzy.FuzzyAttribute(random_email)
#     password = factory.Faker('password')
#
