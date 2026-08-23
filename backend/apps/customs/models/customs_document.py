from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class CustomsDocumentTypeChoices(models.TextChoices):
    COMMERCIAL_INVOICE = 'COMMERCIAL_INVOICE', 'Commercial Invoice'
    PACKING_LIST = 'PACKING_LIST', 'Packing List'
    BILL_OF_LADING = 'BILL_OF_LADING', 'Bill of Lading'
    CERTIFICATE_OF_ORIGIN = 'CERTIFICATE_OF_ORIGIN', 'Certificate of Origin'
    OTHER = 'OTHER', 'Other Supporting Document'


class CustomsClearanceStatusChoices(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted for Clearance'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Customs Review'
    CLEARED = 'CLEARED', 'Customs Cleared'
    REJECTED = 'REJECTED', 'Clearance Rejected'


class ValidationStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending Validation'
    PASSED = 'PASSED', 'Validation Passed'
    FAILED = 'FAILED', 'Validation Failed'


class CustomsDocument(BaseModel):
    """
    Digital customs document entity linked to a shipment (FR-06.1).
    Stores upload file metadata, declared values, validation status, clearance workflow state,
    and audit rejection reasons (FR-06.3).
    """
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='customs_documents',
        db_index=True
    )
    document_type = models.CharField(
        max_length=50,
        choices=CustomsDocumentTypeChoices.choices,
        db_index=True
    )
    file = models.FileField(upload_to='customs_documents/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, default='application/pdf')
    
    document_number = models.CharField(max_length=100, blank=True, help_text="Official invoice or document reference number")
    issue_date = models.DateField(null=True, blank=True)
    declared_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Declared financial value on document in ETB"
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Declared item quantity"
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_customs_documents'
    )
    
    clearance_status = models.CharField(
        max_length=30,
        choices=CustomsClearanceStatusChoices.choices,
        default=CustomsClearanceStatusChoices.DRAFT,
        db_index=True
    )
    validation_status = models.CharField(
        max_length=30,
        choices=ValidationStatusChoices.choices,
        default=ValidationStatusChoices.PENDING,
        db_index=True
    )
    
    validation_notes = models.JSONField(default=dict, blank=True, help_text="Validation result errors or warnings breakdown")
    rejection_reason = models.TextField(blank=True, help_text="Reason provided by customs staff upon rejection")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_customs_documents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Customs Document'
        verbose_name_plural = 'Customs Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shipment', 'document_type']),
            models.Index(fields=['shipment', 'clearance_status']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} for Shipment {self.shipment_id} [{self.clearance_status}]"
