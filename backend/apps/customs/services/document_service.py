from decimal import Decimal
from typing import Optional
from apps.shipments.models import Shipment
from apps.customs.models import CustomsDocument, CustomsClearanceStatusChoices, ValidationStatusChoices
from apps.customs.validators import validate_uploaded_file
from apps.core.exceptions import NotFoundException

def upload_customs_document(
    *,
    shipment_id,
    user,
    document_type,
    file_obj,
    document_number: str = "",
    issue_date = None,
    declared_value: Optional[Decimal] = None,
    quantity: Optional[Decimal] = None
):
    """
    Validates uploaded file constraints and creates a new CustomsDocument record.
    """
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    orig_name, file_size, mime_type = validate_uploaded_file(file_obj)

    doc = CustomsDocument.objects.create(
        shipment=shipment,
        document_type=document_type,
        file=file_obj,
        original_filename=orig_name,
        file_size=file_size,
        mime_type=mime_type,
        document_number=document_number,
        issue_date=issue_date,
        declared_value=declared_value,
        quantity=quantity,
        uploaded_by=user,
        clearance_status=CustomsClearanceStatusChoices.DRAFT,
        validation_status=ValidationStatusChoices.PENDING
    )
    return doc
