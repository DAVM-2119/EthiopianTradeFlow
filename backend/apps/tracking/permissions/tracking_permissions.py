from rest_framework import permissions

class IsShipmentDriverOrParticipant(permissions.BasePermission):
    """
    Permission class for tracking API endpoints:
    - Ingesting GPS data: Requires assigned driver, assigned transporter, or admin.
    - Retrieving tracking history: Requires Shipper, Transporter, Driver, or Admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return True

        shipment = getattr(obj, 'shipment', obj)

        if request.method in permissions.SAFE_METHODS:
            return (
                shipment.shipper == user or
                shipment.transporter == user or
                shipment.driver == user
            )
        else:
            return (
                shipment.driver == user or
                shipment.transporter == user
            )
