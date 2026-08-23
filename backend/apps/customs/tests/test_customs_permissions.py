import pytest
from apps.accounts.models import User, RoleChoices
from apps.customs.permissions import CanViewCustomsDocument, CanReviewCustomsClearance

def test_customs_permissions():
    shipper = User(email="shipper_p@tf.et", role=RoleChoices.SHIPPER)
    customs_staff = User(email="staff_p@tf.et", role=RoleChoices.CUSTOMS_STAFF)
    transporter = User(email="transporter_p@tf.et", role=RoleChoices.TRANSPORTER)

    perm_review = CanReviewCustomsClearance()
    assert perm_review.has_permission(type('Req', (), {'user': customs_staff})(), None) is True
    assert perm_review.has_permission(type('Req', (), {'user': shipper})(), None) is False
    assert perm_review.has_permission(type('Req', (), {'user': transporter})(), None) is False
