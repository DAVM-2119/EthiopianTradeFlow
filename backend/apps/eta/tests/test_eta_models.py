import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.eta.models import ETAPrediction

@pytest.mark.django_db
def test_create_eta_prediction_model():
    shipper = User.objects.create_user(email='shipper_eta_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_eta_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_eta_m@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="ETA Model Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("50000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    pred = ETAPrediction.objects.create(
        shipment=shipment,
        predicted_at=now,
        estimated_arrival=now + timedelta(hours=2),
        remaining_distance_km=Decimal("65.00"),
        expected_speed_kmh=Decimal("50.00"),
        delay_minutes=15,
        prediction_method="RULE_BASED",
        algorithm_version="eta-v1",
        confidence=Decimal("0.85")
    )

    assert pred.shipment == shipment
    assert pred.remaining_distance_km == Decimal("65.00")
    assert "ETA for Shipment" in str(pred)
