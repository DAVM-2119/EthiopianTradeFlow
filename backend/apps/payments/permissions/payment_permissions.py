from rest_framework import permissions

class CanManagePayments(permissions.BasePermission):
    """
    Shipper can create/view own payments. Transporter can view payments/payouts/settlements for own shipments. Admin can view/manage all.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        if request.user.is_staff or user_role == 'ADMIN':
            return True

        if hasattr(obj, 'payer'):
            return obj.payer == request.user or obj.shipment.transporter == request.user
        elif hasattr(obj, 'transporter'):
            return obj.transporter == request.user
        elif hasattr(obj, 'payment'):
            return obj.payment.payer == request.user or obj.payment.shipment.transporter == request.user
        return True


class CanRaiseDispute(permissions.BasePermission):
    """
    Authenticated shipment participant can raise a dispute.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanResolveDispute(permissions.BasePermission):
    """
    Only system administrators can resolve payment disputes.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', '')
        return request.user.is_staff or user_role == 'ADMIN'
