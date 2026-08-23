from rest_framework import permissions

class CanManageRiskZones(permissions.BasePermission):
    """
    Admin, Customs Staff, or staff members can manage RiskZones.
    Read-only for all authenticated users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        user_role = getattr(request.user, 'role', '')
        return request.user.is_staff or user_role in ['ADMIN', 'CUSTOMS_STAFF']


class CanReportIncident(permissions.BasePermission):
    """
    Allows authenticated users (Driver, Transporter, Shipper) to report incidents.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanViewSecurityAlerts(permissions.BasePermission):
    """
    Allows shipment participants (Shipper, Transporter, Driver) or Admin to view alerts.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        if request.user.is_staff or user_role == 'ADMIN':
            return True
        if hasattr(obj, 'shipment') and obj.shipment:
            return (
                obj.shipment.shipper == request.user or
                obj.shipment.transporter == request.user or
                obj.shipment.driver == request.user or
                obj.driver == request.user
            )
        return True
