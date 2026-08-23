from rest_framework import permissions

class IsLoadOwner(permissions.BasePermission):
    """
    Object-level permission checking load.shipper == request.user.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN':
            return True
        return obj.shipper == request.user


class IsBidOwner(permissions.BasePermission):
    """
    Object-level permission checking bid.transporter == request.user.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN':
            return True
        return obj.transporter == request.user
