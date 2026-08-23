from rest_framework import permissions

class CanViewCustomsDocument(permissions.BasePermission):
    """
    Allows Shipper (owner), Freight Forwarder, Customs Staff, or Admin to view customs document.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        if request.user.is_staff or user_role in ('ADMIN', 'CUSTOMS_STAFF', 'FREIGHT_FORWARDER'):
            return True
        return obj.shipment.shipper == request.user


class CanUploadCustomsDocument(permissions.BasePermission):
    """
    Allows Shipper, Freight Forwarder, or Admin to upload customs documents for a shipment.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanReviewCustomsClearance(permissions.BasePermission):
    """
    Allows Customs Staff or Admin to review, approve, or reject clearance submissions.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        return request.user.is_staff or user_role in ('ADMIN', 'CUSTOMS_STAFF')
