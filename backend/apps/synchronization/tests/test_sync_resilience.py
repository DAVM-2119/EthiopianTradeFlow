import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent
from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices

@pytest.mark.django_db
def test_sync_batch_resilience_and_idempotency_recovery():
    driver = User.objects.create_user(email="driver_sync_res@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email="shipper_sync_res@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email="transporter_sync_res@tradeflow.eth", password="Password123!", role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Sync Resilience Load",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(
        load=load,
        transporter=transporter,
        amount=Decimal("90000.00"),
        status=BidStatusChoices.ACCEPTED
    )

    shipment = Shipment.objects.create(
        load=load,
        bid=bid,
        shipper=shipper,
        transporter=transporter,
        driver=driver,
        status=ShipmentStatusChoices.IN_TRANSIT
    )

    client = APIClient()
    client.force_authenticate(user=driver)

    client_evt_1 = str(uuid.uuid4())
    client_evt_2 = str(uuid.uuid4())

    batch_payload = {
        "events": [
            {
                "client_event_id": client_evt_1,
                "event_type": "TRACKING_EVENT",
                "entity_type": "shipment",
                "entity_id": str(shipment.id),
                "payload": {
                    "latitude": 11.5883,
                    "longitude": 43.1450,
                    "speed": 60.0,
                    "heading": 240.0,
                    "recorded_at": now.isoformat()
                },
                "client_created_at": now.isoformat()
            },
            {
                "client_event_id": client_evt_2,
                "event_type": "TRACKING_EVENT",
                "entity_type": "shipment",
                "entity_id": str(shipment.id),
                "payload": {
                    "latitude": 11.4500,
                    "longitude": 43.0000,
                    "speed": 62.5,
                    "heading": 240.0,
                    "recorded_at": (now + timedelta(minutes=5)).isoformat()
                },
                "client_created_at": (now + timedelta(minutes=5)).isoformat()
            }
        ]
    }

    # First Batch Submission
    res1 = client.post('/api/v1/sync/events/batch/', batch_payload, format='json')
    assert res1.status_code == status.HTTP_200_OK
    assert TrackingEvent.objects.filter(shipment=shipment).count() == 2

    # Duplicate Batch Submission (Simulating Mobile Offline Network Retry)
    res2 = client.post('/api/v1/sync/events/batch/', batch_payload, format='json')
    assert res2.status_code == status.HTTP_200_OK
    
    # Assert zero duplicate TrackingEvents created
    assert TrackingEvent.objects.filter(shipment=shipment).count() == 2
    assert OfflineSyncEvent.objects.filter(user=driver, status=SyncStatusChoices.SYNCED).count() == 2
