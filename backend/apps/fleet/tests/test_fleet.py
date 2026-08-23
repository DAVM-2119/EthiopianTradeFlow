import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import (
    Vehicle,
    VehicleTypeChoices,
    CapacityUnitChoices,
    FuelTypeChoices,
    VehicleStatusChoices,
)

@pytest.mark.django_db
def test_transporter_vehicle_crud_success():
    transporter_user = User.objects.create_user(email='t1@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    access_token = str(RefreshToken.for_user(transporter_user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('vehicle-list-create')

    payload = {
        "registration_number": "3-33445-ET",
        "vehicle_type": VehicleTypeChoices.HEAVY_TRUCK,
        "capacity": "45.50",
        "capacity_unit": CapacityUnitChoices.TON,
        "fuel_type": FuelTypeChoices.DIESEL,
        "model": "FH16",
        "manufacturer": "Volvo",
        "year": 2023
    }
    create_resp = client.post(url, payload, format='json')
    assert create_resp.status_code == 201
    v_data = create_resp.json()
    assert v_data['registration_number'] == "3-33445-ET"
    assert v_data['capacity'] == "45.50"
    v_id = v_data['id']

    list_resp = client.get(url)
    assert list_resp.status_code == 200
    results = list_resp.json()['results']
    assert len(results) == 1
    assert results[0]['id'] == v_id

    detail_url = reverse('vehicle-detail', kwargs={'pk': v_id})
    get_resp = client.get(detail_url)
    assert get_resp.status_code == 200
    assert get_resp.json()['model'] == "FH16"

    patch_resp = client.patch(detail_url, {"model": "FH16 Super", "status": VehicleStatusChoices.ASSIGNED}, format='json')
    assert patch_resp.status_code == 200
    assert patch_resp.json()['model'] == "FH16 Super"
    assert patch_resp.json()['status'] == "ASSIGNED"

    del_resp = client.delete(detail_url)
    assert del_resp.status_code == 204
    vehicle = Vehicle.objects.get(id=v_id)
    assert vehicle.status == VehicleStatusChoices.INACTIVE


@pytest.mark.django_db
def test_cross_transporter_vehicle_isolation():
    t1_user = User.objects.create_user(email='t1_iso@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t2_user = User.objects.create_user(email='t2_iso@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    t1_profile, _ = TransporterProfile.objects.get_or_create(user=t1_user)
    t2_profile, _ = TransporterProfile.objects.get_or_create(user=t2_user)

    v1 = Vehicle.objects.create(
        transporter=t1_profile,
        registration_number="3-11111-ET",
        vehicle_type=VehicleTypeChoices.MEDIUM_TRUCK,
        capacity=Decimal("15.00")
    )

    t2_access = str(RefreshToken.for_user(t2_user).access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {t2_access}')

    detail_url = reverse('vehicle-detail', kwargs={'pk': v1.id})
    resp = client.get(detail_url)
    assert resp.status_code in (403, 404)

    list_resp = client.get(reverse('vehicle-list-create'))
    assert list_resp.status_code == 200
    assert len(list_resp.json()['results']) == 0


@pytest.mark.django_db
def test_shipper_cannot_create_vehicle():
    shipper = User.objects.create_user(email='shipper_no_v@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    access_token = str(RefreshToken.for_user(shipper).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('vehicle-list-create')

    payload = {
        "registration_number": "3-99999-ET",
        "vehicle_type": VehicleTypeChoices.HEAVY_TRUCK,
        "capacity": "30.00"
    }
    resp = client.post(url, payload, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_invalid_and_zero_capacity_rejection():
    t_user = User.objects.create_user(email='cap_test@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    access_token = str(RefreshToken.for_user(t_user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('vehicle-list-create')

    payload = {
        "registration_number": "3-00000-ET",
        "vehicle_type": VehicleTypeChoices.HEAVY_TRUCK,
        "capacity": "0.00"
    }
    resp = client.post(url, payload, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_duplicate_registration_number_rejection():
    t_user = User.objects.create_user(email='dup_test@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user)

    Vehicle.objects.create(
        transporter=t_prof,
        registration_number="3-UNIQUE-ET",
        vehicle_type=VehicleTypeChoices.HEAVY_TRUCK,
        capacity=Decimal("30.00")
    )

    access_token = str(RefreshToken.for_user(t_user).access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('vehicle-list-create')

    payload = {
        "registration_number": "3-UNIQUE-ET",
        "vehicle_type": VehicleTypeChoices.HEAVY_TRUCK,
        "capacity": "20.00"
    }
    resp = client.post(url, payload, format='json')
    assert resp.status_code == 400
