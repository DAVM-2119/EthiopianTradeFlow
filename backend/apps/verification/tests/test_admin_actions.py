import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import ShipperProfile
from apps.verification.models import Verification, VerificationStatusChoices, VerificationHistory
from apps.verification.services import submit_verification

@pytest.mark.django_db
def test_admin_approve_and_suspend_workflow():
    shipper = User.objects.create_user(email='shipper_wf@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    prof, _ = ShipperProfile.objects.get_or_create(user=shipper)
    prof.business_name = "Shipper Ltd"
    prof.trade_license_number = "TL-200"
    prof.tax_id = "TIN-200"
    prof.save()

    verification = submit_verification(shipper)
    assert verification.status == VerificationStatusChoices.PENDING

    admin = User.objects.create_superuser(email='admin_wf@tradeflow.et', password='Password123!')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(admin).access_token}')

    approve_url = reverse('admin-verification-approve', kwargs={'pk': verification.id})
    app_resp = client.post(approve_url, {"reason": "All documents valid"}, format='json')
    assert app_resp.status_code == 200

    verification.refresh_from_db()
    shipper.refresh_from_db()
    assert verification.status == VerificationStatusChoices.VERIFIED
    assert shipper.is_verified is True
    assert VerificationHistory.objects.filter(verification=verification).count() == 2

    suspend_url = reverse('admin-verification-suspend', kwargs={'pk': verification.id})
    sus_resp = client.post(suspend_url, {"reason": "License expired"}, format='json')
    assert sus_resp.status_code == 200

    verification.refresh_from_db()
    shipper.refresh_from_db()
    assert verification.status == VerificationStatusChoices.SUSPENDED
    assert shipper.is_verified is False
    assert VerificationHistory.objects.filter(verification=verification).count() == 3


@pytest.mark.django_db
def test_non_admin_cannot_approve_or_suspend():
    shipper = User.objects.create_user(email='shipper_sec@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    prof, _ = ShipperProfile.objects.get_or_create(user=shipper)
    prof.business_name = "Shipper Ltd"
    prof.trade_license_number = "TL-300"
    prof.tax_id = "TIN-300"
    prof.save()
    verification = submit_verification(shipper)

    other_user = User.objects.create_user(email='other@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(other_user).access_token}')

    approve_url = reverse('admin-verification-approve', kwargs={'pk': verification.id})
    response = client.post(approve_url, {"reason": "Attempt"}, format='json')
    assert response.status_code == 403
