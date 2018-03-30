from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """ Base Manager for our Models. Creates users
    with e-mail address, password and all your extra fields. """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """ Creation and saving User Model instance to database happens here. """
        if not email:
            raise ValueError('Email must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        if hasattr(self.model, 'is_staff'):
            extra_fields.setdefault('is_staff', False)
        if hasattr(self.model, 'is_superuser'):
            extra_fields.setdefault('is_superuser', False)
        if hasattr(self.model, 'is_active'):
            extra_fields.setdefault('is_active', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        if hasattr(self.model, 'is_staff'):
            extra_fields.setdefault('is_staff', True)
        if hasattr(self.model, 'is_superuser'):
            extra_fields.setdefault('is_superuser', True)
        if hasattr(self.model, 'is_active'):
            extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)
