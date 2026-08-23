from rest_framework.permissions import BasePermission
from apps.accounts.models.user import StatusChoices

class IsActiveAccount(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.status != StatusChoices.SUSPENDED and
            request.user.status != StatusChoices.INACTIVE
        )


class IsNotSuspendedAccount(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.status != StatusChoices.SUSPENDED
        )


class IsVerifiedAccount(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )
