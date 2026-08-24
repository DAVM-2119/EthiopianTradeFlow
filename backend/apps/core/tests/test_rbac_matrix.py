import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices

@pytest.mark.django_db
def test_comprehensive_rbac_and_object_level_permission_matrix():
    # 1. Create multi-role users
    shipper_a = User.objects.create_user(email="shipper_a@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER, is_verified=True)
    shipper_b = User.objects.create_user(email="shipper_b@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER, is_verified=True)
    transporter = User.objects.create_user(email="transporter_rbac@tradeflow.eth", password="Password123!", role=RoleChoices.TRANSPORTER, is_verified=True)
    driver_a = User.objects.create_user(email="driver_a@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER, is_verified=True)
    driver_b = User.objects.create_user(email="driver_b@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER, is_verified=True)
    customs_staff = User.objects.create_user(email="customs_staff@tradeflow.eth", password="Password123!", role=RoleChoices.CUSTOMS_STAFF, is_verified=True)
    admin = User.objects.create_user(email="admin_rbac@tradeflow.eth", password="Password123!", role=RoleChoices.ADMIN, is_staff=True, is_superuser=True)

    now = timezone.now()
    load_a = Load.objects.create(
        shipper=shipper_a,
        title="Shipper A Freight",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    load_b = Load.objects.create(
        shipper=shipper_b,
        title="Shipper B Freight",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid_a = Bid.objects.create(load=load_a, transporter=transporter, amount=Decimal("60000.00"), status=BidStatusChoices.ACTIVE)
    shipment_a = Shipment.objects.create(load=load_a, bid=bid_a, shipper=shipper_a, transporter=transporter, driver=driver_a, status=ShipmentStatusChoices.IN_TRANSIT)

    client = APIClient()

    # Rule 1: Shipper B cannot cancel Shipper A's load (Object Ownership)
    client.force_authenticate(user=shipper_b)
    cancel_resp = client.post(f'/api/v1/loads/{load_a.id}/cancel/')
    assert cancel_resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    # Rule 2: Driver B cannot view Driver A's private shipment details
    client.force_authenticate(user=driver_b)
    shipment_resp = client.get(f'/api/v1/shipments/{shipment_a.id}/')
    assert shipment_resp.status_code == status.HTTP_403_FORBIDDEN

    # Rule 3: Driver A can view assigned shipment
    client.force_authenticate(user=driver_a)
    shipment_ok = client.get(f'/api/v1/shipments/{shipment_a.id}/')
    assert shipment_ok.status_code == status.HTTP_200_OK

    # Rule 4: Customs staff cannot post marketplace loads
    client.force_authenticate(user=customs_staff)
    post_load_resp = client.post('/api/v1/loads/', {
        "title": "Customs Illegal Load",
        "origin_city": "Djibouti",
        "destination_city": "Modjo",
        "cargo_type": "DRY_BULK",
        "weight": "10.00",
        "pickup_window_start": now.isoformat(),
        "pickup_window_end": (now + timedelta(days=1)).isoformat()
    })
    assert post_load_resp.status_code == status.HTTP_403_FORBIDDEN

    # Rule 5: Admin user has full access
    client.force_authenticate(user=admin)
    admin_resp = client.get(f'/api/v1/shipments/{shipment_a.id}/')
    assert admin_resp.status_code == status.HTTP_200_OK
