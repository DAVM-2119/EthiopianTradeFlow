from rest_framework import permissions

class CanViewFuelAnalytics(permissions.BasePermission):
    """
    Allows Transporter (owner of vehicle/driver/shipment), Driver (own metrics), Shipper (own shipment), or Admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        if request.user.is_staff or user_role == 'ADMIN':
            return True
        if hasattr(obj, 'shipment'):
            return obj.shipment.transporter == request.user or obj.shipment.driver == request.user or obj.shipment.shipper == request.user
        return True


class CanRecordFuelData(permissions.BasePermission):
    """
    Allows Transporter, Driver assigned to shipment, or Admin to record fuel data.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanViewTransporterPerformance(permissions.BasePermission):
    """
    Transporter can view own performance analytics. Admin can view any transporter.
    Unauthorized users are denied access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        return user_role in ['TRANSPORTER', 'ADMIN'] or request.user.is_staff
