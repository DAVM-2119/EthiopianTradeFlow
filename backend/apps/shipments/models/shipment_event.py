from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ShipmentEvent(BaseModel):
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='events',
        db_index=True
    )
    event_type = models.CharField(max_length=50, help_text="Event type tag, e.g. STATUS_TRANSITION, ASSIGNMENT, POD_SUBMITTED")
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    description = models.TextField(help_text="Human-readable description of event")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_shipment_events'
    )

    class Meta:
        verbose_name = 'Shipment Event'
        verbose_name_plural = 'Shipment Events'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['shipment', 'created_at']),
        ]

    def __str__(self):
        return f"Event #{self.id} on Shipment {self.shipment_id}: {self.previous_status} -> {self.new_status}"
