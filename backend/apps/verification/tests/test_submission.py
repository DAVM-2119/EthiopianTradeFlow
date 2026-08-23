import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import ShipperProfile
from apps.verification.models import Verification, VerificationStatusChoices, VerificationHistory

@pytest.mark.django_db
def test_shipper_verification_submission_success():
    shipper = User.objects.create_user(email='shipper_v@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    prof, _ = ShipperProfile.objects.get_or_create(user=shipper)
    prof.business_name = "Shipper Ltd"
    prof.trade_license_number = "TL-100"
    prof.tax_id = "TIN-100"
    prof.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')
    url = reverse('verification-submit')

    response = client.post(url, format='json')
    assert response.status_code == 201
    data = response.json()['data']
    assert data['status'] == VerificationStatusChoices.PENDING

    verification = Verification.objects.get(user=shipper)
    assert verification.status == VerificationStatusChoices.PENDING
    assert VerificationHistory.objects.filter(verification=verification).count() == 1


@pytest.mark.django_db
def test_submission_incomplete_profile_rejected():
    shipper = User.objects.create_user(email='incomplete@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')
    url = reverse('verification-submit')

    response = client.post(url, format='json')
    assert response.status_code == 400
    assert "incomplete" in response.json()['error']['message'].lower()
