import pytest
from apps.accounts.models import User, RoleChoices
from apps.payments.permissions import CanManagePayments, CanRaiseDispute, CanResolveDispute

def test_payment_permissions():
    admin = User(email="admin_perm@tradeflow.et", role=RoleChoices.ADMIN)
    shipper = User(email="shipper_perm@tradeflow.et", role=RoleChoices.SHIPPER)
    transporter = User(email="transporter_perm@tradeflow.et", role=RoleChoices.TRANSPORTER)

    p_manage = CanManagePayments()
    p_raise = CanRaiseDispute()
    p_resolve = CanResolveDispute()

    assert p_manage.has_permission(type('Req', (), {'user': shipper})(), None) is True
    assert p_raise.has_permission(type('Req', (), {'user': transporter})(), None) is True

    assert p_resolve.has_permission(type('Req', (), {'user': admin})(), None) is True
    assert p_resolve.has_permission(type('Req', (), {'user': shipper})(), None) is False
