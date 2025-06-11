from rest_framework import permissions
from ..models import Privilege


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.privilege.name == Privilege.OWNER
        )


class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.privilege.name == Privilege.EDITOR
        )
