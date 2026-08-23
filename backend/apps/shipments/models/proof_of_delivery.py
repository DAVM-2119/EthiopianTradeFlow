from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ProofOfDelivery(BaseModel):
    shipment = models.OneToOneField(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='proof_of_delivery',
        db_index=True
    )
    receiver_name = models.CharField(max_length=255, help_text="Full name of person accepting delivery")
    delivery_timestamp = models.DateTimeField(help_text="Timestamp when cargo was physically received")
    signature_reference = models.CharField(max_length=512, blank=True, help_text="Reference URI/path or digital signature hash")
    photo_reference = models.CharField(max_length=512, blank=True, help_text="Reference URI/path to proof photo")
    notes = models.TextField(blank=True, help_text="Delivery confirmation notes or condition comments")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_pods'
    )

    class Meta:
        verbose_name = 'Proof of Delivery'
        verbose_name_plural = 'Proofs of Delivery'

    def __str__(self):
        return f"POD for Shipment {self.shipment_id} - Received by {self.receiver_name}"
