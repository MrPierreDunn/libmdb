from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка разрешений для админа."""

    def has_permission(self, request, view):
        """Переопределение разрешения."""
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )
