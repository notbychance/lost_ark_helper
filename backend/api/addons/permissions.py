from rest_framework import permissions
from ..models import GroupParticipants


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return GroupParticipants.objects.filter(group=obj, user=request.user).exists()
