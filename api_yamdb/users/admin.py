from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as Admin

from users.models import User


@register(User)
class UserAdmin(Admin):
    """Пользователь админка."""

    list_display = ('email', 'username', 'role')
    empty_value_display = '-empty-'
