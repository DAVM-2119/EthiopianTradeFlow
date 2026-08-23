import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.customs.models import (
    CustomsDocument,
    CustomsDocumentTypeChoices,
    CustomsClearanceStatusChoices,
    ValidationStatusChoices,
)

@pytest.mark.django_db
def test_create_customs_document_model():
    shipper = User.objects.create_user(email='shipper_cust_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_cust_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_cust_m@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Customs Model Load",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        weight=Decimal("35.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("90000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    dummy_file = SimpleUploadedFile("invoice.pdf", b"PDF dummy content", content_type="application/pdf")

    doc = CustomsDocument.objects.create(
        shipment=shipment,
        document_type=CustomsDocumentTypeChoices.COMMERCIAL_INVOICE,
        file=dummy_file,
        original_filename="invoice.pdf",
        file_size=len(b"PDF dummy content"),
        mime_type="application/pdf",
        document_number="INV-2026-001",
        declared_value=Decimal("150000.00"),
        quantity=Decimal("100.00"),
        uploaded_by=shipper,
        clearance_status=CustomsClearanceStatusChoices.DRAFT,
        validation_status=ValidationStatusChoices.PENDING
    )

    assert doc.shipment == shipment
    assert doc.document_type == CustomsDocumentTypeChoices.COMMERCIAL_INVOICE
    assert doc.declared_value == Decimal("150000.00")
    assert doc.clearance_status == CustomsClearanceStatusChoices.DRAFT
    assert "Commercial Invoice for Shipment" in str(doc)
