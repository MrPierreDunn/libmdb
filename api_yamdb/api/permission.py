from rest_framework import permissions
from users.models import User


class AdminAnonPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.role == User.ADMIN or request.user.is_staff))


class IsOwnerOrAdminOrModerator(permissions.BasePermission):
    """Пермишен для автора, модератора и админа"""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.role in [User.ADMIN, User.MODERATOR])
