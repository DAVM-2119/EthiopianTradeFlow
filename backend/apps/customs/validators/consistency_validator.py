from typing import List, Dict, Tuple
from apps.customs.models import CustomsDocument, CustomsDocumentTypeChoices

REQUIRED_CLEARANCE_DOCUMENTS = {
    CustomsDocumentTypeChoices.COMMERCIAL_INVOICE,
    CustomsDocumentTypeChoices.PACKING_LIST,
    CustomsDocumentTypeChoices.BILL_OF_LADING,
    CustomsDocumentTypeChoices.CERTIFICATE_OF_ORIGIN,
}

def validate_customs_consistency(documents: List[CustomsDocument]) -> Tuple[bool, List[Dict[str, str]]]:
    """
    FR-06.2 Automated validation:
    1. Checks required document completeness (Commercial Invoice, Packing List, Bill of Lading, Certificate of Origin).
    2. Checks cross-document consistency (Commercial Invoice quantity vs Packing List quantity, declared values).
    Returns (is_valid, list_of_error_dicts).
    """
    errors: List[Dict[str, str]] = []

    uploaded_types = {doc.document_type for doc in documents}
    missing_types = REQUIRED_CLEARANCE_DOCUMENTS - uploaded_types

    for missing in missing_types:
        label = dict(CustomsDocumentTypeChoices.choices).get(missing, missing)
        errors.append({
            "code": f"MISSING_{missing}",
            "message": f"Required customs document missing: {label}."
        })

    invoices = [d for d in documents if d.document_type == CustomsDocumentTypeChoices.COMMERCIAL_INVOICE]
    packing_lists = [d for d in documents if d.document_type == CustomsDocumentTypeChoices.PACKING_LIST]

    if invoices and packing_lists:
        inv = invoices[0]
        pkg = packing_lists[0]

        if inv.quantity is not None and pkg.quantity is not None and inv.quantity != pkg.quantity:
            errors.append({
                "code": "QUANTITY_MISMATCH",
                "message": f"Invoice quantity ({inv.quantity}) does not match Packing List quantity ({pkg.quantity})."
            })

        if inv.declared_value is None or inv.declared_value <= 0:
            errors.append({
                "code": "INVALID_DECLARED_VALUE",
                "message": "Commercial Invoice must specify a valid declared value greater than zero."
            })

    is_valid = (len(errors) == 0)
    return is_valid, errors
