import pytest
from apps.accounts.models import User, RoleChoices
from apps.analytics.permissions import CanViewTransporterPerformance

def test_performance_permissions():
    admin = User(email="admin_perf_p@tf.et", role=RoleChoices.ADMIN)
    transporter = User(email="transporter_perf_p@tf.et", role=RoleChoices.TRANSPORTER)
    shipper = User(email="shipper_perf_p@tf.et", role=RoleChoices.SHIPPER)

    perm = CanViewTransporterPerformance()

    assert perm.has_permission(type('Req', (), {'user': admin, 'method': 'GET'})(), None) is True
    assert perm.has_permission(type('Req', (), {'user': transporter, 'method': 'GET'})(), None) is True
    assert perm.has_permission(type('Req', (), {'user': shipper, 'method': 'GET'})(), None) is False
