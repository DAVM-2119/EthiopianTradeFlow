import pytest
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.exceptions import ValidationException
from apps.customs.models import CustomsDocument, CustomsDocumentTypeChoices
from apps.customs.validators import validate_uploaded_file, validate_customs_consistency

def test_document_file_validation():
    valid_file = SimpleUploadedFile("invoice.pdf", b"PDF content", content_type="application/pdf")
    name, size, mime = validate_uploaded_file(valid_file)
    assert name == "invoice.pdf"
    assert size == len(b"PDF content")

    invalid_ext = SimpleUploadedFile("script.exe", b"binary content", content_type="application/octet-stream")
    with pytest.raises(ValidationException):
        validate_uploaded_file(invalid_ext)

def test_consistency_validation_missing_documents():
    d1 = CustomsDocument(document_type=CustomsDocumentTypeChoices.COMMERCIAL_INVOICE, quantity=Decimal("50.00"), declared_value=Decimal("10000.00"))
    is_valid, errors = validate_customs_consistency([d1])
    assert is_valid is False
    assert len(errors) == 3

def test_consistency_validation_quantity_mismatch():
    d1 = CustomsDocument(document_type=CustomsDocumentTypeChoices.COMMERCIAL_INVOICE, quantity=Decimal("50.00"), declared_value=Decimal("10000.00"))
    d2 = CustomsDocument(document_type=CustomsDocumentTypeChoices.PACKING_LIST, quantity=Decimal("40.00"))
    d3 = CustomsDocument(document_type=CustomsDocumentTypeChoices.BILL_OF_LADING)
    d4 = CustomsDocument(document_type=CustomsDocumentTypeChoices.CERTIFICATE_OF_ORIGIN)

    is_valid, errors = validate_customs_consistency([d1, d2, d3, d4])
    assert is_valid is False
    assert any(e['code'] == 'QUANTITY_MISMATCH' for e in errors)
