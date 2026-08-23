import pytest
from unittest.mock import MagicMock
from apps.accounts.models import RoleChoices, StatusChoices
from apps.accounts.permissions import (
    IsAdmin,
    IsShipper,
    IsTransporter,
    IsDriver,
    IsFreightForwarder,
    IsCustomsStaff,
    HasAnyRole,
    IsActiveAccount,
    IsNotSuspendedAccount,
)

def test_role_based_permissions():
    shipper = MagicMock(is_authenticated=True, role=RoleChoices.SHIPPER, is_staff=False)
    admin = MagicMock(is_authenticated=True, role=RoleChoices.ADMIN, is_staff=True)
    driver = MagicMock(is_authenticated=True, role=RoleChoices.DRIVER, is_staff=False)

    assert IsShipper().has_permission(MagicMock(user=shipper), None) is True
    assert IsShipper().has_permission(MagicMock(user=admin), None) is False

    assert IsAdmin().has_permission(MagicMock(user=admin), None) is True
    assert IsAdmin().has_permission(MagicMock(user=shipper), None) is False

    assert IsDriver().has_permission(MagicMock(user=driver), None) is True
    assert IsDriver().has_permission(MagicMock(user=shipper), None) is False

    has_roles_perm = HasAnyRole(allowed_roles=(RoleChoices.SHIPPER, RoleChoices.TRANSPORTER))
    assert has_roles_perm.has_permission(MagicMock(user=shipper), MagicMock()) is True
    assert has_roles_perm.has_permission(MagicMock(user=driver), MagicMock()) is False


def test_account_status_permissions():
    active_user = MagicMock(is_authenticated=True, is_active=True, status=StatusChoices.ACTIVE)
    suspended_user = MagicMock(is_authenticated=True, is_active=True, status=StatusChoices.SUSPENDED)
    inactive_user = MagicMock(is_authenticated=True, is_active=False, status=StatusChoices.INACTIVE)

    assert IsActiveAccount().has_permission(MagicMock(user=active_user), None) is True
    assert IsActiveAccount().has_permission(MagicMock(user=suspended_user), None) is False
    assert IsActiveAccount().has_permission(MagicMock(user=inactive_user), None) is False

    assert IsNotSuspendedAccount().has_permission(MagicMock(user=active_user), None) is True
    assert IsNotSuspendedAccount().has_permission(MagicMock(user=suspended_user), None) is False
