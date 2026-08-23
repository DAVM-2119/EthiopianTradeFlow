import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices, ShipmentEvent
from apps.shipments.services import transition_shipment

@pytest.mark.django_db
def test_shipment_events_audit_log():
    shipper = User.objects.create_user(email='shipper_se@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_se@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Event Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("30000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.BOOKED)

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.ASSIGNED, actor=transporter)
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.PICKUP_READY, actor=transporter)

    events = ShipmentEvent.objects.filter(shipment=shipment).order_by('created_at')
    assert events.count() == 2
    assert events[0].new_status == ShipmentStatusChoices.ASSIGNED
    assert events[1].new_status == ShipmentStatusChoices.PICKUP_READY
