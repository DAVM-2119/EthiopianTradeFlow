import pytest
import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.synchronization.services import process_sync_event, retry_failed_sync_event
from apps.synchronization.models import SyncStatusChoices

@pytest.mark.django_db
def test_sync_service_retry_and_failed_handling():
    driver = User.objects.create_user(email='driver_service@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    shipper = User.objects.create_user(email='shipper_service@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_service@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Service Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("10.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("20000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    invalid_data = {
        'client_event_id': uuid.uuid4(),
        'event_type': 'TRACKING_EVENT',
        'entity_type': 'shipment',
        'entity_id': shipment.id,
        'payload': {'speed': 50.0},
        'client_created_at': now
    }

    evt = process_sync_event(user=driver, data=invalid_data)
    assert evt.status == SyncStatusChoices.FAILED
    assert evt.error_code == 'KeyError'

    evt.payload = {
        'latitude': 8.9800,
        'longitude': 38.7500,
        'recorded_at': now.isoformat()
    }
    evt.save()

    retried_evt = retry_failed_sync_event(user=driver, client_event_id=evt.client_event_id)
    assert retried_evt.status == SyncStatusChoices.SYNCED
    assert retried_evt.attempt_count == 2
