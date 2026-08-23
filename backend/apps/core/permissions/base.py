from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaffUser(BasePermission):
    """
    Allows access only to authenticated staff / admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ReadOnly(BasePermission):
    """
    Allows read-only access for SAFE_METHODS (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Generic object-level permission allowing read-only access to anyone,
    and write access to the owner of the object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'actor_id'):
            return str(obj.actor_id) == str(getattr(request.user, 'id', ''))

        return False
