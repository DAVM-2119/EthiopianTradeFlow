import pytest
from apps.accounts.models import User, RoleChoices
from apps.analytics.permissions import CanViewFuelAnalytics, CanRecordFuelData

def test_analytics_permissions():
    shipper = User(email="shipper_perm@tf.et", role=RoleChoices.SHIPPER)
    driver = User(email="driver_perm@tf.et", role=RoleChoices.DRIVER)
    transporter = User(email="transporter_perm@tf.et", role=RoleChoices.TRANSPORTER)

    perm_view = CanViewFuelAnalytics()
    perm_record = CanRecordFuelData()

    assert perm_view.has_permission(type('Req', (), {'user': shipper})(), None) is True
    assert perm_record.has_permission(type('Req', (), {'user': driver})(), None) is True
