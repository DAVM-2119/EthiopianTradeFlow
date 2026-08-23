import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import (
    ShipperProfile,
    TransporterProfile,
    DriverProfile,
    FreightForwarderProfile,
    CustomsStaffProfile,
)

@pytest.mark.django_db
def test_shipper_profile_retrieval_and_update():
    user = User.objects.create_user(email='shipper_prof@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    access_token = str(RefreshToken.for_user(user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('profile-me')

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json()['data']['country'] == 'Ethiopia'

    patch_payload = {
        "business_name": "Addis Import Export PLC",
        "trade_license_number": "TL-998877",
        "city": "Addis Ababa"
    }
    patch_resp = client.patch(url, patch_payload, format='json')
    assert patch_resp.status_code == 200
    assert patch_resp.json()['data']['business_name'] == "Addis Import Export PLC"

    profile = ShipperProfile.objects.get(user=user)
    assert profile.business_name == "Addis Import Export PLC"
    assert profile.trade_license_number == "TL-998877"


@pytest.mark.django_db
def test_transporter_profile_and_driver_fleet_management():
    transporter_user = User.objects.create_user(email='transporter_prof@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    access_token = str(RefreshToken.for_user(transporter_user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    me_resp = client.get(reverse('profile-me'))
    assert me_resp.status_code == 200

    driver_user = User.objects.create_user(email='driver_prof@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    drivers_url = reverse('transporter-drivers')

    post_resp = client.post(drivers_url, {
        "user": str(driver_user.id),
        "license_number": "ETH-DL-112233",
        "license_type": "Heavy Freight Level 4",
        "emergency_contact_name": "Taye",
        "emergency_contact_phone": "+251911000111"
    }, format='json')
    assert post_resp.status_code == 201
    assert post_resp.json()['license_number'] == "ETH-DL-112233"

    driver_profile = DriverProfile.objects.get(license_number="ETH-DL-112233")
    transporter_profile = TransporterProfile.objects.get(user=transporter_user)
    assert driver_profile.transporter == transporter_profile


@pytest.mark.django_db
def test_profile_one_to_one_constraint_and_role_protection():
    user = User.objects.create_user(email='one_to_one@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    p1 = ShipperProfile.objects.create(user=user, business_name="P1")
    with pytest.raises(Exception):
        ShipperProfile.objects.create(user=user, business_name="P2")
