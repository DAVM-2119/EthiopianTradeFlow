from rest_framework import permissions

class IsNotificationRecipient(permissions.BasePermission):
    """
    Enforces strict user isolation.
    Users can only access notifications and preferences where they are the recipient or user.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user or request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'

        return False
