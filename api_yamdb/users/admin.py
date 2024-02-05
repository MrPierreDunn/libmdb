from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from users.models import User


@register(User)
class UserAdmin(UserAdmin):
    """Пользователь админка."""

    list_display = ('email', 'username', 'role')
    empty_value_display = '-empty-'
