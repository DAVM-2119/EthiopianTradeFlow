from django.db import models
from apps.core.models import BaseModel

class DocumentTypeChoices(models.TextChoices):
    INSURANCE = 'INSURANCE', 'Insurance Policy'
    ROADWORTHINESS = 'ROADWORTHINESS', 'Roadworthiness Certificate'
    REGISTRATION = 'REGISTRATION', 'Vehicle Registration Ownership'


class DocumentStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VALID = 'VALID', 'Valid'
    EXPIRED = 'EXPIRED', 'Expired'


class VehicleDocument(BaseModel):
    vehicle = models.ForeignKey(
        'fleet.Vehicle',
        on_delete=models.CASCADE,
        related_name='documents',
        db_index=True
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentTypeChoices.choices,
        db_index=True
    )
    document_number = models.CharField(max_length=100)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatusChoices.choices,
        default=DocumentStatusChoices.PENDING,
        db_index=True
    )

    class Meta:
        verbose_name = 'Vehicle Document'
        verbose_name_plural = 'Vehicle Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document_type} - {self.document_number} ({self.vehicle.registration_number})"
