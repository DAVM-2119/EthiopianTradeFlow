import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import ShipperProfile
from apps.verification.models import Verification, VerificationStatusChoices, VerificationHistory
from apps.verification.services import approve_verification

@pytest.mark.django_db
def test_cross_user_verification_privacy_isolation():
    u1 = User.objects.create_user(email='u1_priv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    u2 = User.objects.create_user(email='u2_priv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    Verification.objects.create(user=u1, status=VerificationStatusChoices.PENDING)
    Verification.objects.create(user=u2, status=VerificationStatusChoices.VERIFIED)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(u1).access_token}')

    me_resp = client.get(reverse('verification-me'))
    assert me_resp.status_code == 200
    assert me_resp.json()['data']['user_email'] == 'u1_priv@tradeflow.et'

    admin_resp = client.get(reverse('admin-verification-queue'))
    assert admin_resp.status_code == 403


@pytest.mark.django_db
def test_transaction_rollback_on_history_creation_failure():
    shipper = User.objects.create_user(email='rollback@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    prof, _ = ShipperProfile.objects.get_or_create(user=shipper)
    prof.business_name = "Rollback Ltd"
    prof.trade_license_number = "TL-900"
    prof.tax_id = "TIN-900"
    prof.save()

    verification = Verification.objects.create(user=shipper, status=VerificationStatusChoices.PENDING)
    admin = User.objects.create_superuser(email='admin_rb@tradeflow.et', password='Password123!')

    with patch('apps.verification.models.VerificationHistory.objects.create', side_effect=Exception("Database error")):
        with pytest.raises(Exception):
            approve_verification(admin, verification.id, "Test Reason")

    verification.refresh_from_db()
    shipper.refresh_from_db()
    assert verification.status == VerificationStatusChoices.PENDING
    assert shipper.is_verified is False
