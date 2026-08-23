from rest_framework.permissions import BasePermission
from apps.accounts.models.user import RoleChoices

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == RoleChoices.ADMIN or request.user.is_staff))


class IsShipper(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.SHIPPER)


class IsTransporter(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.TRANSPORTER)


class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.DRIVER)


class IsFreightForwarder(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.FREIGHT_FORWARDER)


class IsCustomsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == RoleChoices.CUSTOMS_STAFF)


class HasAnyRole(BasePermission):
    """
    Role check allowing access if user's role is in allowed_roles set on view or passed in.
    """
    allowed_roles = ()

    def __init__(self, allowed_roles=None):
        if allowed_roles is not None:
            self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        view_roles = getattr(view, 'allowed_roles', None)
        if view_roles is not None and isinstance(view_roles, (list, tuple, set)):
            roles = view_roles
        else:
            roles = self.allowed_roles

        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in roles
        )
