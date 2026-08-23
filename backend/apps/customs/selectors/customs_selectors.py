from apps.customs.models import CustomsDocument, CustomsClearanceStatusChoices

def get_customs_documents_for_shipment(shipment_id):
    """
    Retrieves all customs documents for a shipment.
    """
    return CustomsDocument.objects.filter(shipment_id=shipment_id).order_by('-created_at')


def get_customs_document_by_id(doc_id):
    """
    Retrieves customs document by UUID primary key.
    """
    return CustomsDocument.objects.filter(id=doc_id).first()


def get_clearance_status_for_shipment(shipment_id):
    """
    Summarizes customs clearance workflow status for a shipment.
    """
    docs = CustomsDocument.objects.filter(shipment_id=shipment_id)
    if not docs.exists():
        return {
            "status": CustomsClearanceStatusChoices.DRAFT,
            "document_count": 0,
            "can_submit": False
        }

    statuses = [d.clearance_status for d in docs]
    if all(s == CustomsClearanceStatusChoices.CLEARED for s in statuses):
        overall = CustomsClearanceStatusChoices.CLEARED
    elif any(s == CustomsClearanceStatusChoices.REJECTED for s in statuses):
        overall = CustomsClearanceStatusChoices.REJECTED
    elif any(s == CustomsClearanceStatusChoices.UNDER_REVIEW for s in statuses):
        overall = CustomsClearanceStatusChoices.UNDER_REVIEW
    elif any(s == CustomsClearanceStatusChoices.SUBMITTED for s in statuses):
        overall = CustomsClearanceStatusChoices.SUBMITTED
    else:
        overall = CustomsClearanceStatusChoices.DRAFT

    return {
        "status": overall,
        "document_count": docs.count(),
        "can_submit": overall in (CustomsClearanceStatusChoices.DRAFT, CustomsClearanceStatusChoices.REJECTED)
    }
