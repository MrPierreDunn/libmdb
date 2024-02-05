from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re

from users.constsans import (
    MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH, MAX_LAST_NAME_LENGTH,
    MAX_USERNAME_LENGTH, MAX_ROLE_LENGTH
)


def validate_username_uniqueness(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError(
            ('Пользователь с таким username уже существует.'),
            params={'value': value},
        )
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" не разрешено.'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Недопустимые символы :', re.sub(r'[\w.@+-]+', '', value)
        )


class User(AbstractUser):
    """Модель пользователя"""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    STAFF = 'staff'
    SUPERUSER = 'superuser'
    USER_ROLE = [
        ('user', USER),
        ('admin', ADMIN),
        ('moderator', MODERATOR),
        ('staff', STAFF),
        ('superuser', SUPERUSER)
    ]

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[validate_username_uniqueness]
    )
    email = models.EmailField(
        'E-mail',
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    first_name = models.TextField(
        'Имя',
        max_length=MAX_FIRST_NAME_LENGTH,
        blank=True
    )
    last_name = models.TextField(
        'Фамилия',
        max_length=MAX_LAST_NAME_LENGTH,
        blank=True
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль пользователя',
        max_length=MAX_ROLE_LENGTH,
        choices=USER_ROLE,
        default='user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', 'role',)
