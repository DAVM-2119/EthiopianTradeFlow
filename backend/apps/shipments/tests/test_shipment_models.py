import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices

@pytest.mark.django_db
def test_shipment_model_defaults_and_relationships():
    shipper = User.objects.create_user(email='shipper_sm@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_sm@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Test Load for Shipment",
        origin_city="Addis Ababa",
        destination_city="Hawassa",
        weight=Decimal("10.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(
        load=load,
        transporter=transporter,
        amount=Decimal("20000.00"),
        status=BidStatusChoices.ACCEPTED,
        accepted_at=now
    )

    shipment = Shipment.objects.create(
        load=load,
        bid=bid,
        shipper=shipper,
        transporter=transporter,
        status=ShipmentStatusChoices.BOOKED
    )

    assert shipment.status == ShipmentStatusChoices.BOOKED
    assert shipment.load == load
    assert shipment.bid == bid
    assert shipment.shipper == shipper
    assert shipment.transporter == transporter
    assert shipment.vehicle is None
    assert shipment.driver is None
