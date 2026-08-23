from rest_framework import permissions

class IsMatchOwnerOrAdmin(permissions.BasePermission):
    """
    Permission allowing Load owner, target Transporter, or Admin to view match recommendation.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN':
            return True
        return obj.load.shipper == request.user or obj.transporter == request.user
