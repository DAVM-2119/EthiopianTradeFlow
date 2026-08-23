import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent
from apps.tracking.services import record_tracking_event
from apps.core.exceptions import ValidationException, ConflictException, PermissionDeniedException

@pytest.mark.django_db
def test_tracking_service_recording_validation_and_duplicate_prevention():
    shipper = User.objects.create_user(email='shipper_ts@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_ts@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver_a = User.objects.create_user(email='driver_a_ts@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    driver_b = User.objects.create_user(email='driver_b_ts@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Tracking Service Load",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("70000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver_a, status=ShipmentStatusChoices.IN_TRANSIT)

    event1 = record_tracking_event(
        shipment_id=shipment.id,
        driver_user=driver_a,
        latitude=Decimal("11.588000"),
        longitude=Decimal("43.145000"),
        speed=Decimal("75.00"),
        heading=Decimal("180.00"),
        recorded_at=now,
        event_id="gps-evt-001"
    )
    assert event1.id is not None
    assert event1.event_id == "gps-evt-001"

    event1_dup = record_tracking_event(
        shipment_id=shipment.id,
        driver_user=driver_a,
        latitude=Decimal("11.588000"),
        longitude=Decimal("43.145000"),
        speed=Decimal("75.00"),
        heading=Decimal("180.00"),
        recorded_at=now,
        event_id="gps-evt-001"
    )
    assert event1_dup.id == event1.id
    assert TrackingEvent.objects.filter(shipment=shipment).count() == 1

    with pytest.raises(PermissionDeniedException):
        record_tracking_event(
            shipment_id=shipment.id,
            driver_user=driver_b,
            latitude=Decimal("11.588000"),
            longitude=Decimal("43.145000"),
            recorded_at=now
        )

    with pytest.raises(ValidationException):
        record_tracking_event(
            shipment_id=shipment.id,
            driver_user=driver_a,
            latitude=Decimal("105.000000"),
            longitude=Decimal("43.145000"),
            recorded_at=now
        )

    with pytest.raises(ValidationException):
        record_tracking_event(
            shipment_id=shipment.id,
            driver_user=driver_a,
            latitude=Decimal("11.588000"),
            longitude=Decimal("200.000000"),
            recorded_at=now
        )

    shipment.status = ShipmentStatusChoices.COMPLETED
    shipment.save()

    with pytest.raises(ConflictException):
        record_tracking_event(
            shipment_id=shipment.id,
            driver_user=driver_a,
            latitude=Decimal("11.588000"),
            longitude=Decimal("43.145000"),
            recorded_at=now
        )
