from rest_framework import permissions

from reviews.models import ADMIN


class AdminAnonPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.role == ADMIN or request.user.is_staff))
