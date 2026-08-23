from rest_framework import permissions

class IsShipmentParticipantOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing Shipper, Transporter, Driver, or Admin to access shipment.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN':
            return True
        return (
            obj.shipper == request.user or
            obj.transporter == request.user or
            obj.driver == request.user
        )
