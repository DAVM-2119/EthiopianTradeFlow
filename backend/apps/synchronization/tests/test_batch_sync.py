import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.synchronization.services import process_batch_sync_events
from apps.synchronization.models import SyncStatusChoices

@pytest.mark.django_db
def test_batch_sync_processing():
    driver = User.objects.create_user(email='driver_batch@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email='shipper_batch@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_batch@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Batch Sync Test Load",
        origin_city="Addis Ababa",
        destination_city="Dire Dawa",
        weight=Decimal("22.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("60000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    id3 = uuid.uuid4()

    batch_payload = [
        {
            'client_event_id': id1,
            'event_type': 'WAYPOINT_CHECKIN',
            'entity_type': 'shipment',
            'entity_id': shipment.id,
            'payload': {'notes': 'Checkin at Mojo', 'latitude': 8.90, 'longitude': 38.70, 'recorded_at': now.isoformat()},
            'client_created_at': now
        },
        {
            'client_event_id': id2,
            'event_type': 'INCIDENT_REPORT',
            'entity_type': 'shipment',
            'entity_id': shipment.id,
            'payload': {'incident_type': 'ROAD_BLOCK', 'description': 'Road maintenance delay', 'latitude': 8.95, 'longitude': 38.75, 'recorded_at': (now + timedelta(minutes=5)).isoformat()},
            'client_created_at': now + timedelta(minutes=5)
        },
        {
            'client_event_id': id3,
            'event_type': 'TRACKING_EVENT',
            'entity_type': 'shipment',
            'entity_id': shipment.id,
            'payload': {'latitude': 9.00, 'longitude': 38.80, 'speed': 55.0, 'heading': 90.0, 'recorded_at': (now + timedelta(minutes=10)).isoformat()},
            'client_created_at': now + timedelta(minutes=10)
        }
    ]

    results = process_batch_sync_events(user=driver, events_data=batch_payload)
    assert len(results) == 3
    assert results[0]['status'] == SyncStatusChoices.SYNCED
    assert results[1]['status'] == SyncStatusChoices.SYNCED
    assert results[2]['status'] == SyncStatusChoices.SYNCED
