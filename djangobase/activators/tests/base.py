from ..base import BaseEmailActivator
from ..email import UserRegistrationActivator


class BaseEmailActivatorTestClass(BaseEmailActivator):
    email_body_template = 'email_activators/BaseEmailActivator_body.txt'
    email_subject_template = 'email_activators/BaseEmailActivator_subject.txt'


class UserRegistrationActivatorTestClass(UserRegistrationActivator):
    email_body_template = 'email_activators/UserRegistrationActivator_body.txt'
    email_subject_template = 'email_activators/UserRegistrationActivator_subject.txt'
