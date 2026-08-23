from django.utils import timezone
from django.db import transaction
from apps.verification.models import Verification, VerificationHistory, VerificationStatusChoices
from apps.profiles.services import get_or_create_user_profile
from apps.accounts.models import RoleChoices
from apps.core.exceptions import ValidationException, NotFoundException, ConflictException
from apps.verification.services.eligibility_service import is_vehicle_verification_eligible
from apps.fleet.models import Vehicle

def submit_verification(user):
    """
    Self-service verification submission. Validates profile completeness & transporter fleet requirements.
    Sets status to PENDING and logs VerificationHistory atomically.
    """
    profile_obj, _ = get_or_create_user_profile(user)

    missing_fields = []
    if user.role in (RoleChoices.SHIPPER, RoleChoices.TRANSPORTER, RoleChoices.FREIGHT_FORWARDER):
        for field in ['trade_license_number', 'tax_id', 'business_name']:
            if not getattr(profile_obj, field, None):
                missing_fields.append(field)
    elif user.role == RoleChoices.DRIVER:
        for field in ['license_number', 'license_type']:
            if not getattr(profile_obj, field, None):
                missing_fields.append(field)

    if missing_fields:
        raise ValidationException(
            message="Profile is incomplete.",
            details={"missing_fields": missing_fields}
        )

    if user.role == RoleChoices.TRANSPORTER:
        vehicles = Vehicle.objects.filter(transporter=profile_obj)
        if not vehicles.exists():
            raise ValidationException("Transporters must register at least one vehicle before submitting verification.")

        has_eligible_vehicle = any(is_vehicle_verification_eligible(v) for v in vehicles)
        if not has_eligible_vehicle:
            raise ValidationException("At least one vehicle in fleet must have valid, unexpired insurance, roadworthiness, and registration documents.")

    with transaction.atomic():
        verification, created = Verification.objects.get_or_create(user=user)

        if not created and verification.status == VerificationStatusChoices.VERIFIED:
            raise ConflictException("User is already verified.")

        previous_status = verification.status
        now = timezone.now()

        verification.status = VerificationStatusChoices.PENDING
        verification.submitted_at = now
        verification.save()

        VerificationHistory.objects.create(
            verification=verification,
            previous_status=previous_status,
            new_status=VerificationStatusChoices.PENDING,
            changed_by=user,
            reason="Submitted for verification",
            notes=f"Submitted by user {user.email}"
        )

    return verification


def approve_verification(admin_user, verification_id, reason="Approved by administrator", notes=""):
    """
    Admin approves verification. Sets status = VERIFIED, user.is_verified = True, and appends history atomically.
    """
    verification = Verification.objects.select_related('user').filter(id=verification_id).first()
    if not verification:
        raise NotFoundException("Verification record not found.")

    with transaction.atomic():
        previous_status = verification.status
        now = timezone.now()

        verification.status = VerificationStatusChoices.VERIFIED
        verification.verified_at = now
        verification.save()

        user = verification.user
        user.is_verified = True
        user.save(update_fields=['is_verified'])

        VerificationHistory.objects.create(
            verification=verification,
            previous_status=previous_status,
            new_status=VerificationStatusChoices.VERIFIED,
            changed_by=admin_user,
            reason=reason,
            notes=notes
        )

    return verification


def suspend_verification(admin_user, verification_id, reason, notes=""):
    """
    Admin suspends verification. Requires a non-empty reason.
    Sets status = SUSPENDED, user.is_verified = False, and appends history atomically.
    """
    if not reason or not reason.strip():
        raise ValidationException("A valid reason is required for suspension.")

    verification = Verification.objects.select_related('user').filter(id=verification_id).first()
    if not verification:
        raise NotFoundException("Verification record not found.")

    with transaction.atomic():
        previous_status = verification.status
        now = timezone.now()

        verification.status = VerificationStatusChoices.SUSPENDED
        verification.suspended_at = now
        verification.save()

        user = verification.user
        user.is_verified = False
        user.save(update_fields=['is_verified'])

        VerificationHistory.objects.create(
            verification=verification,
            previous_status=previous_status,
            new_status=VerificationStatusChoices.SUSPENDED,
            changed_by=admin_user,
            reason=reason.strip(),
            notes=notes
        )

    return verification


def reject_verification(admin_user, verification_id, reason, notes=""):
    """
    Admin rejects verification. Requires a non-empty reason.
    Sets status = REJECTED, user.is_verified = False, and appends history atomically.
    """
    if not reason or not reason.strip():
        raise ValidationException("A valid reason is required for rejection.")

    verification = Verification.objects.select_related('user').filter(id=verification_id).first()
    if not verification:
        raise NotFoundException("Verification record not found.")

    with transaction.atomic():
        previous_status = verification.status

        verification.status = VerificationStatusChoices.REJECTED
        verification.save()

        user = verification.user
        user.is_verified = False
        user.save(update_fields=['is_verified'])

        VerificationHistory.objects.create(
            verification=verification,
            previous_status=previous_status,
            new_status=VerificationStatusChoices.REJECTED,
            changed_by=admin_user,
            reason=reason.strip(),
            notes=notes
        )

    return verification
