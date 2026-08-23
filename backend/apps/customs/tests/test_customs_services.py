import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.customs.models import CustomsDocument, CustomsDocumentTypeChoices, CustomsClearanceStatusChoices
from apps.customs.services import (
    upload_customs_document,
    validate_shipment_customs_documents,
    submit_customs_clearance,
    update_customs_clearance_status
)

@pytest.mark.django_db
def test_customs_services_workflow():
    shipper = User.objects.create_user(email='shipper_cust_s@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_cust_s@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_cust_s@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    customs_staff = User.objects.create_user(email='customs_staff_s@tradeflow.et', password='Password123!', role=RoleChoices.CUSTOMS_STAFF)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Customs Service Load",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        weight=Decimal("40.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("100000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    docs = []
    types_data = [
        (CustomsDocumentTypeChoices.COMMERCIAL_INVOICE, "inv.pdf", Decimal("100.00"), Decimal("200000.00")),
        (CustomsDocumentTypeChoices.PACKING_LIST, "pack.pdf", Decimal("100.00"), None),
        (CustomsDocumentTypeChoices.BILL_OF_LADING, "bol.pdf", None, None),
        (CustomsDocumentTypeChoices.CERTIFICATE_OF_ORIGIN, "coo.pdf", None, None),
    ]

    for dtype, fname, qty, val in types_data:
        f = SimpleUploadedFile(fname, b"PDF content", content_type="application/pdf")
        doc = upload_customs_document(
            shipment_id=shipment.id, user=shipper, document_type=dtype, file_obj=f, quantity=qty, declared_value=val
        )
        docs.append(doc)

    assert len(docs) == 4

    val_res = validate_shipment_customs_documents(shipment_id=shipment.id)
    assert val_res['valid'] is True
    assert val_res['validation_status'] == 'PASSED'

    sub_res = submit_customs_clearance(shipment_id=shipment.id, user=shipper)
    assert sub_res['status'] == CustomsClearanceStatusChoices.SUBMITTED
    shipment.refresh_from_db()
    assert shipment.status == ShipmentStatusChoices.CUSTOMS_PROCESSING

    rev_res = update_customs_clearance_status(
        shipment_id=shipment.id, reviewer_user=customs_staff, new_status=CustomsClearanceStatusChoices.CLEARED
    )
    assert rev_res['status'] == CustomsClearanceStatusChoices.CLEARED
    shipment.refresh_from_db()
    assert shipment.status == ShipmentStatusChoices.CUSTOMS_CLEARED
