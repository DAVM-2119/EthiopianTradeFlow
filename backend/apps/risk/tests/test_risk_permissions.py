import pytest
from apps.accounts.models import User, RoleChoices
from apps.risk.permissions import CanManageRiskZones, CanReportIncident, CanViewSecurityAlerts

def test_risk_permissions():
    admin = User(email="admin_p@tf.et", role=RoleChoices.ADMIN)
    shipper = User(email="shipper_p@tf.et", role=RoleChoices.SHIPPER)
    driver = User(email="driver_p@tf.et", role=RoleChoices.DRIVER)

    perm_manage = CanManageRiskZones()
    perm_report = CanReportIncident()

    req_admin = type('Req', (), {'user': admin, 'method': 'POST'})()
    req_shipper = type('Req', (), {'user': shipper, 'method': 'POST'})()

    assert perm_manage.has_permission(req_admin, None) is True
    assert perm_manage.has_permission(req_shipper, None) is False
    assert perm_report.has_permission(type('Req', (), {'user': driver})(), None) is True
