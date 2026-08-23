import pytest
from decimal import Decimal
from datetime import date, timedelta
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.verification.services import (
    is_vehicle_verification_eligible,
    is_transporter_marketplace_eligible,
    is_marketplace_eligible,
)

@pytest.mark.django_db
def test_vehicle_and_transporter_eligibility_rules():
    t_user = User.objects.create_user(email='transporter_el@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user)

    v1 = Vehicle.objects.create(
        transporter=t_prof,
        registration_number="3-ELIG-ET",
        vehicle_type=VehicleTypeChoices.HEAVY_TRUCK,
        capacity=Decimal("30.00")
    )

    assert is_vehicle_verification_eligible(v1) is False

    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-1", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)

    assert is_vehicle_verification_eligible(v1) is True

    verification, _ = Verification.objects.get_or_create(user=t_user, status=VerificationStatusChoices.PENDING)
    assert is_transporter_marketplace_eligible(t_prof) is False
    assert is_marketplace_eligible(t_user) is False

    verification.status = VerificationStatusChoices.VERIFIED
    verification.save()
    assert is_transporter_marketplace_eligible(t_prof) is True
    assert is_marketplace_eligible(t_user) is True


@pytest.mark.django_db
def test_expired_document_invalidates_vehicle_eligibility():
    t_user = User.objects.create_user(email='exp_el@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=t_user)

    v1 = Vehicle.objects.create(
        transporter=t_prof,
        registration_number="3-EXPIRED-ET",
        vehicle_type=VehicleTypeChoices.HEAVY_TRUCK,
        capacity=Decimal("30.00")
    )

    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=365)

    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-2", status=DocumentStatusChoices.VALID, expiry_date=yesterday)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-2", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v1, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-2", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)

    assert is_vehicle_verification_eligible(v1) is False
