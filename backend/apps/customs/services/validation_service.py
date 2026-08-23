from typing import Dict, Any
from django.db import transaction
from apps.shipments.models import Shipment
from apps.customs.models import CustomsDocument, ValidationStatusChoices
from apps.customs.validators import validate_customs_consistency
from apps.core.exceptions import NotFoundException

def validate_shipment_customs_documents(*, shipment_id) -> Dict[str, Any]:
    """
    FR-06.2 Runs document completeness and cross-document consistency checks on shipment customs documents.
    Updates validation_status and validation_notes on all documents.
    """
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    docs = list(CustomsDocument.objects.filter(shipment=shipment))
    is_valid, errors = validate_customs_consistency(docs)

    val_status = ValidationStatusChoices.PASSED if is_valid else ValidationStatusChoices.FAILED
    val_notes = {"errors": errors}

    with transaction.atomic():
        CustomsDocument.objects.filter(shipment=shipment).update(
            validation_status=val_status,
            validation_notes=val_notes
        )

    return {
        "valid": is_valid,
        "validation_status": val_status,
        "errors": errors,
        "document_count": len(docs)
    }
