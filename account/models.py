from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.crypto import get_random_string

# All my models here.

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            return ValueError('Mail should definitely be handed over')
        email = self.normalize_email(email=email)
        user = self.model(email = email, **kwargs)
        phone_number = kwargs.get('phone_number')
        if phone_number:
            user.create_phone_number_code()
        else:
            user.create_activation_code()
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)
    
    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        if kwargs.get('is_staff') is not True:
            raise ValueError('У пользователя должны быть права is_staff = True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('У пользователя должны быть права is_superuser = True')
        return self._create_user(email, password, **kwargs)


class CustomUser(AbstractUser):
    email = models.EmailField(unique = True)
    password = models.CharField(max_length = 100)
    activation_code = models.CharField(max_length = 255, blank = True)
    username = models.CharField(max_length = 100, blank = True)
    first_name = models.CharField(max_length = 100)
    avatar = models.ImageField(upload_to='avatars', blank = True)
    is_active = models.BooleanField(default = False, help_text='This field id to activate user')
    phone_number = models.CharField(max_length = 25, blank = True, null = True, unique = True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email
    
    def create_activation_code(self):
        import uuid
        code = str(uuid.uuid4())
        self.activation_code = code

    def create_phone_number_code(self):
        code = get_random_string(6, allowed_chars = '123456789')
        self.activation_code = code
        return code
