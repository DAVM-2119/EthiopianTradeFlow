import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.shipments.services import transition_shipment, record_proof_of_delivery
from apps.core.exceptions import ConflictException, ValidationException

@pytest.mark.django_db
def test_valid_and_invalid_shipment_state_transitions():
    shipper = User.objects.create_user(email='shipper_st@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_st@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Transition Load",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("100000.00"), status=BidStatusChoices.ACCEPTED)

    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.BOOKED)

    with pytest.raises(ConflictException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.DELIVERED, actor=transporter)

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.ASSIGNED, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.ASSIGNED

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.PICKUP_READY, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.PICKUP_READY

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.IN_TRANSIT, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.IN_TRANSIT

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.DELIVERED, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.DELIVERED

    with pytest.raises(ValidationException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.COMPLETED, actor=transporter)

    record_proof_of_delivery(
        shipment=shipment,
        actor=transporter,
        receiver_name="Abebe Bikila",
        delivery_timestamp=now
    )

    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.COMPLETED, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.COMPLETED
