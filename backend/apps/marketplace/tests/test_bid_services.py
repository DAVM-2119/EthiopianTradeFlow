import pytest
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.marketplace.services import create_bid, update_bid_service, withdraw_bid, accept_bid
from apps.core.exceptions import PermissionDeniedException, ConflictException

@pytest.fixture
def verified_transporter():
    t_user = User.objects.create_user(email='verified_t@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user)
    v1 = Vehicle.objects.create(transporter=t_prof, registration_number="3-V1-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-V1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-V1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-V1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=t_user, status=VerificationStatusChoices.VERIFIED)
    return t_user

@pytest.mark.django_db
def test_unverified_transporter_cannot_create_bid():
    shipper = User.objects.create_user(email='shipper_unv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    unverified_t = User.objects.create_user(email='unverified_t@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Posted Load",
        origin_city="Addis Ababa",
        destination_city="Adama",
        weight=Decimal("10.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    with pytest.raises(PermissionDeniedException):
        create_bid(transporter_user=unverified_t, load_id=load.id, validated_data={"amount": Decimal("10000.00")})


@pytest.mark.django_db
def test_verified_transporter_bidding_and_acceptance_workflow(verified_transporter):
    shipper = User.objects.create_user(email='shipper_acc@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t2 = User.objects.create_user(email='verified_t2@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t2_prof, _ = TransporterProfile.objects.get_or_create(user=t2)
    v2 = Vehicle.objects.create(transporter=t2_prof, registration_number="3-V2-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v2, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-V2", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v2, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-V2", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v2, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-V2", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=t2, status=VerificationStatusChoices.VERIFIED)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Posted Load for Bidding",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    b1 = create_bid(transporter_user=verified_transporter, load_id=load.id, validated_data={"amount": Decimal("120000.00")})
    assert b1.status == BidStatusChoices.ACTIVE

    b2 = create_bid(transporter_user=t2, load_id=load.id, validated_data={"amount": Decimal("115000.00")})
    assert b2.status == BidStatusChoices.ACTIVE

    accepted = accept_bid(bid_id=b2.id, load_owner_user=shipper)
    assert accepted.status == BidStatusChoices.ACCEPTED

    load.refresh_from_db()
    b1.refresh_from_db()

    assert load.status == LoadStatusChoices.BOOKED
    assert b1.status == BidStatusChoices.REJECTED

    with pytest.raises(ConflictException):
        accept_bid(bid_id=b1.id, load_owner_user=shipper)
