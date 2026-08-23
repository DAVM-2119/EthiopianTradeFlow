import pytest
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.matching.services import generate_matches
from apps.matching.models import MatchRecommendation
from apps.core.exceptions import PermissionDeniedException, ConflictException

@pytest.fixture
def verified_transporter_factory():
    def _create_transporter(email, city="Addis Ababa"):
        t_user = User.objects.create_user(email=email, password='Password123!', role=RoleChoices.TRANSPORTER)
        t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user, city=city)
        v = Vehicle.objects.create(transporter=t_prof, registration_number=f"3-{email[:4]}-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
        tomorrow = date.today() + timedelta(days=365)
        VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.INSURANCE, document_number="INS", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
        VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
        VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
        Verification.objects.create(user=t_user, status=VerificationStatusChoices.VERIFIED)
        return t_user
    return _create_transporter

@pytest.mark.django_db
def test_matching_service_candidate_filtering_and_ranking(verified_transporter_factory):
    shipper = User.objects.create_user(email='shipper_ms@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t1 = verified_transporter_factory('t1_ms@tradeflow.et', city="Addis Ababa")
    t2 = verified_transporter_factory('t2_ms@tradeflow.et', city="Hawassa")

    unverified_t = User.objects.create_user(email='unverified_ms@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Freight Load for Matching",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    matches = generate_matches(load_id=load.id, requesting_user=shipper)

    transporter_ids = [m.transporter_id for m in matches]
    assert unverified_t.id not in transporter_ids

    assert len(matches) == 2
    assert matches[0].rank == 1
    assert matches[1].rank == 2
    assert matches[0].transporter_id == t1.id

    generate_matches(load_id=load.id, requesting_user=shipper)
    active_count = MatchRecommendation.objects.filter(load=load, is_active=True).count()
    inactive_count = MatchRecommendation.objects.filter(load=load, is_active=False).count()

    assert active_count == 2
    assert inactive_count == 2
