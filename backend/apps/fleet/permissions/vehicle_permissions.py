from rest_framework.permissions import BasePermission
from apps.accounts.models import RoleChoices

class IsVehicleOwner(BasePermission):
    """
    Object-level permission ensuring vehicle.transporter.user == request.user or admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and (request.user.role == RoleChoices.ADMIN or request.user.is_staff):
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(obj, 'transporter') and
            obj.transporter.user == request.user
        )
