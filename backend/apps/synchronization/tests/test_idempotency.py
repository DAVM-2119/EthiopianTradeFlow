import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent
from apps.synchronization.services import process_sync_event
from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices

@pytest.mark.django_db
def test_idempotency_duplicate_event_returns_existing_synced_record():
    driver = User.objects.create_user(email='driver_idemp@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email='shipper_idemp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_idemp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Idempotency Test Load",
        origin_city="Addis Ababa",
        destination_city="Adama",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("30000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    client_event_id = uuid.uuid4()
    data = {
        'client_event_id': client_event_id,
        'event_type': 'TRACKING_EVENT',
        'entity_type': 'shipment',
        'entity_id': shipment.id,
        'payload': {
            'latitude': 8.980600,
            'longitude': 38.757800,
            'speed': 45.0,
            'heading': 180.0,
            'recorded_at': now.isoformat()
        },
        'client_created_at': now
    }

    evt1 = process_sync_event(user=driver, data=data)
    assert evt1.status == SyncStatusChoices.SYNCED
    tracking_count_1 = TrackingEvent.objects.filter(shipment=shipment).count()
    assert tracking_count_1 == 1

    evt2 = process_sync_event(user=driver, data=data)
    assert evt2.status == SyncStatusChoices.SYNCED
    assert evt2.id == evt1.id

    tracking_count_2 = TrackingEvent.objects.filter(shipment=shipment).count()
    assert tracking_count_2 == 1
