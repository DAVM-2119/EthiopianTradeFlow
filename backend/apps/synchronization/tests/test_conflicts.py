import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.services import record_tracking_event
from apps.synchronization.services import process_sync_event
from apps.synchronization.models import SyncStatusChoices

@pytest.mark.django_db
def test_stale_event_marked_conflict():
    driver = User.objects.create_user(email='driver_conflict@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email='shipper_conflict@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_conflict@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Conflict Test Load",
        origin_city="Addis Ababa",
        destination_city="Awash",
        weight=Decimal("18.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("40000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    newer_time = now + timedelta(minutes=10)
    record_tracking_event(
        shipment_id=shipment.id,
        driver_user=driver,
        latitude=Decimal("8.980000"),
        longitude=Decimal("38.750000"),
        recorded_at=newer_time,
        event_id="newer-evt-100"
    )

    stale_data = {
        'client_event_id': uuid.uuid4(),
        'event_type': 'TRACKING_EVENT',
        'entity_type': 'shipment',
        'entity_id': shipment.id,
        'payload': {
            'latitude': 8.900000,
            'longitude': 38.700000,
            'recorded_at': now.isoformat()
        },
        'client_created_at': now
    }

    evt = process_sync_event(user=driver, data=stale_data)
    assert evt.status == SyncStatusChoices.CONFLICT
    assert evt.error_code == "STALE_TIMESTAMP"
