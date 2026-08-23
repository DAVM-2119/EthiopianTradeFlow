from datetime import date
from apps.fleet.models import Vehicle, VehicleDocument, DocumentTypeChoices, DocumentStatusChoices, VehicleStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.accounts.models import RoleChoices

def is_vehicle_verification_eligible(vehicle):
    """
    Evaluates whether a single vehicle satisfies verification requirements.
    Requires presence of valid, unexpired INSURANCE, ROADWORTHINESS, and REGISTRATION documents.
    """
    if vehicle.status == VehicleStatusChoices.INACTIVE:
        return False

    required_types = {
        DocumentTypeChoices.INSURANCE,
        DocumentTypeChoices.ROADWORTHINESS,
        DocumentTypeChoices.REGISTRATION
    }

    today = date.today()
    valid_docs = VehicleDocument.objects.filter(
        vehicle=vehicle,
        status=DocumentStatusChoices.VALID,
        document_type__in=required_types
    )

    found_types = set()
    for doc in valid_docs:
        if doc.expiry_date and doc.expiry_date < today:
            continue
        found_types.add(doc.document_type)

    return required_types.issubset(found_types)


def is_transporter_marketplace_eligible(transporter_profile):
    """
    Evaluates whether a transporter profile is marketplace eligible.
    Requires user verification status == VERIFIED AND at least 1 verified-eligible vehicle.
    """
    user = transporter_profile.user
    verification = getattr(user, 'verification', None)
    if not verification or verification.status != VerificationStatusChoices.VERIFIED:
        return False

    vehicles = Vehicle.objects.filter(transporter=transporter_profile, status=VehicleStatusChoices.AVAILABLE)
    return any(is_vehicle_verification_eligible(v) for v in vehicles)


def is_marketplace_eligible(user):
    """
    Generic entrypoint checking if user is marketplace transaction eligible.
    """
    if not user.is_authenticated or not user.is_active:
        return False

    verification = getattr(user, 'verification', None)
    if not verification or verification.status != VerificationStatusChoices.VERIFIED:
        return False

    if user.role == RoleChoices.TRANSPORTER and hasattr(user, 'transporter_profile'):
        return is_transporter_marketplace_eligible(user.transporter_profile)

    return True
