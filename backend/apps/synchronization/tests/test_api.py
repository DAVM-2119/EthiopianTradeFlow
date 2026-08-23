import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.synchronization.models import SyncStatusChoices

@pytest.mark.django_db
def test_sync_api_endpoints():
    driver = User.objects.create_user(email='driver_api_sync@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email='shipper_api_sync@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_api_sync@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Sync API Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("12.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("25000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    client = APIClient()
    token = str(RefreshToken.for_user(driver).access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    client_id = uuid.uuid4()
    payload = {
        'client_event_id': str(client_id),
        'device_id': 'driver-phone-1',
        'event_type': 'WAYPOINT_CHECKIN',
        'entity_type': 'shipment',
        'entity_id': str(shipment.id),
        'payload': {
            'notes': 'Passed Gelan checkpoint',
            'latitude': 8.9000,
            'longitude': 38.7500,
            'recorded_at': now.isoformat()
        },
        'client_created_at': now.isoformat()
    }

    res1 = client.post('/api/v1/sync/events/', data=payload, format='json')
    assert res1.status_code == status.HTTP_201_CREATED
    assert res1.data['data']['status'] == SyncStatusChoices.SYNCED

    res2 = client.get(f'/api/v1/sync/events/{client_id}/')
    assert res2.status_code == status.HTTP_200_OK
    assert res2.data['data']['client_event_id'] == str(client_id)

    res3 = client.get('/api/v1/sync/status/')
    assert res3.status_code == status.HTTP_200_OK
    assert res3.data['data']['synced'] >= 1
