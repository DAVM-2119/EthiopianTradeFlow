import pytest
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.shipments.services import transition_shipment, record_proof_of_delivery
from apps.core.exceptions import ConflictException, ValidationException
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices

@pytest.mark.django_db
def test_shipment_state_machine_valid_and_invalid_transitions():
    shipper = User.objects.create_user(email="shipper_sm@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email="transporter_sm@tradeflow.eth", password="Password123!", role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email="driver_sm@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="State Machine Freight",
        origin_city="Djibouti",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(
        load=load,
        transporter=transporter,
        amount=Decimal("75000.00"),
        status=BidStatusChoices.ACCEPTED
    )

    shipment = Shipment.objects.create(
        load=load,
        bid=bid,
        shipper=shipper,
        transporter=transporter,
        status=ShipmentStatusChoices.BOOKED
    )

    # 1. Invalid jump: BOOKED -> DELIVERED (must fail)
    with pytest.raises(ConflictException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.DELIVERED, actor=transporter)

    # 2. Invalid jump: BOOKED -> IN_TRANSIT (must fail)
    with pytest.raises(ConflictException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.IN_TRANSIT, actor=transporter)

    # 3. Valid transition: BOOKED -> ASSIGNED
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.ASSIGNED, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.ASSIGNED

    # 4. Valid transition: ASSIGNED -> PICKUP_READY
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.PICKUP_READY, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.PICKUP_READY

    # 5. Valid transition: PICKUP_READY -> IN_TRANSIT
    shipment.driver = driver
    shipment.save()
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.IN_TRANSIT, actor=driver)
    assert shipment.status == ShipmentStatusChoices.IN_TRANSIT

    # 6. Invalid jump: IN_TRANSIT -> COMPLETED (without POD and DELIVERED status)
    with pytest.raises(ConflictException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.COMPLETED, actor=driver)

    # 7. Valid transition: IN_TRANSIT -> DELIVERED
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.DELIVERED, actor=driver)
    assert shipment.status == ShipmentStatusChoices.DELIVERED

    # 8. Invalid transition: DELIVERED -> COMPLETED without recorded POD (must fail ValidationException)
    with pytest.raises(ValidationException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.COMPLETED, actor=transporter)

    # 9. Record POD
    record_proof_of_delivery(
        shipment=shipment,
        actor=driver,
        receiver_name="Modjo Gate Officer",
        delivery_timestamp=now
    )

    # 10. Valid transition: DELIVERED -> COMPLETED (with POD)
    transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.COMPLETED, actor=transporter)
    assert shipment.status == ShipmentStatusChoices.COMPLETED

    # 11. Invalid jump from COMPLETED -> ASSIGNED or IN_TRANSIT (terminal state)
    with pytest.raises(ConflictException):
        transition_shipment(shipment=shipment, target_status=ShipmentStatusChoices.IN_TRANSIT, actor=transporter)
