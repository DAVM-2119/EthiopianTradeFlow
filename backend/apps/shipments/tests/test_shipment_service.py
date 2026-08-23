import pytest
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.marketplace.services import accept_bid, create_bid
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.shipments.services import assign_shipment_resources
from apps.core.exceptions import ValidationException

@pytest.fixture
def verified_transporter():
    t_user = User.objects.create_user(email='verified_t_ss@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user)
    v1 = Vehicle.objects.create(transporter=t_prof, registration_number="3-VSS-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.INSURANCE, document_number="INS", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=t_user, status=VerificationStatusChoices.VERIFIED)
    return t_user, v1

@pytest.mark.django_db
def test_bid_acceptance_automatically_creates_shipment(verified_transporter):
    t_user, vehicle = verified_transporter
    shipper = User.objects.create_user(email='shipper_ss@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    driver = User.objects.create_user(email='driver_ss@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Freight Load for Shipment Test",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = create_bid(transporter_user=t_user, load_id=load.id, validated_data={"amount": Decimal("50000.00")})
    
    accepted_bid = accept_bid(bid_id=bid.id, load_owner_user=shipper)
    
    shipment = Shipment.objects.filter(load=load).first()
    assert shipment is not None
    assert shipment.status == ShipmentStatusChoices.BOOKED
    assert shipment.shipper == shipper
    assert shipment.transporter == t_user

    assigned = assign_shipment_resources(
        shipment=shipment,
        actor=t_user,
        vehicle_id=vehicle.id,
        driver_id=driver.id
    )
    assert assigned.status == ShipmentStatusChoices.ASSIGNED
    assert assigned.vehicle == vehicle
    assert assigned.driver == driver
