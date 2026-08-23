from typing import Optional
from django.utils import timezone
from django.db import transaction
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.customs.models import CustomsDocument, CustomsClearanceStatusChoices
from apps.customs.validators import validate_customs_consistency
from apps.customs.providers import MockCustomsProvider
from apps.core.exceptions import NotFoundException, ValidationException

def submit_customs_clearance(*, shipment_id, user, provider=None):
    """
    FR-06.3 Submits validated customs documents for clearance review (DRAFT -> SUBMITTED -> UNDER_REVIEW).
    """
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    docs = list(CustomsDocument.objects.filter(shipment=shipment))
    if not docs:
        raise ValidationException("Cannot submit customs clearance without uploading required documents.")

    is_valid, errors = validate_customs_consistency(docs)
    if not is_valid:
        error_msgs = [e['message'] for e in errors]
        raise ValidationException(f"Customs validation failed: {'; '.join(error_msgs)}")

    if provider is None:
        provider = MockCustomsProvider()

    doc_ids = [str(d.id) for d in docs]
    res = provider.submit_for_clearance(str(shipment.id), doc_ids)

    with transaction.atomic():
        CustomsDocument.objects.filter(shipment=shipment).update(
            clearance_status=CustomsClearanceStatusChoices.SUBMITTED,
            rejection_reason=""
        )
        shipment.status = ShipmentStatusChoices.CUSTOMS_PROCESSING
        shipment.customs_processing_at = timezone.now()
        shipment.save(update_fields=['status', 'customs_processing_at', 'updated_at'])

    return {
        "shipment_id": str(shipment.id),
        "status": CustomsClearanceStatusChoices.SUBMITTED,
        "reference_number": res.reference_number,
        "message": res.message
    }


def update_customs_clearance_status(*, shipment_id, reviewer_user, new_status, rejection_reason: str = ""):
    """
    FR-06.3 Customs Staff or Admin review workflow transition (UNDER_REVIEW -> CLEARED / REJECTED).
    """
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    if new_status == CustomsClearanceStatusChoices.REJECTED and not rejection_reason.strip():
        raise ValidationException("Rejection reason is required when rejecting customs clearance.")

    now = timezone.now()
    with transaction.atomic():
        CustomsDocument.objects.filter(shipment=shipment).update(
            clearance_status=new_status,
            rejection_reason=rejection_reason if new_status == CustomsClearanceStatusChoices.REJECTED else "",
            reviewed_by=reviewer_user,
            reviewed_at=now
        )

        if new_status == CustomsClearanceStatusChoices.CLEARED:
            shipment.status = ShipmentStatusChoices.CUSTOMS_CLEARED
            shipment.customs_cleared_at = now
            shipment.save(update_fields=['status', 'customs_cleared_at', 'updated_at'])

    return {
        "shipment_id": str(shipment.id),
        "status": new_status,
        "rejection_reason": rejection_reason,
        "reviewed_at": now
    }
