import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.services import record_tracking_event
from apps.eta.services import calculate_and_save_eta
from apps.eta.selectors import get_latest_eta_prediction

@pytest.mark.django_db
def test_calculate_and_save_eta_service():
    shipper = User.objects.create_user(email='shipper_eta_srv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_eta_srv@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_eta_srv@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="ETA Service Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("55000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    record_tracking_event(
        shipment_id=shipment.id,
        driver_user=driver,
        latitude=Decimal("9.000000"),
        longitude=Decimal("38.750000"),
        speed=Decimal("55.00"),
        heading=Decimal("90.00"),
        recorded_at=now,
        event_id="eta-track-001"
    )

    prediction = calculate_and_save_eta(shipment_id=shipment.id)
    assert prediction is not None
    assert prediction.shipment == shipment
    assert prediction.expected_speed_kmh == Decimal("55.00")

    latest = get_latest_eta_prediction(shipment.id)
    assert latest.id == prediction.id
