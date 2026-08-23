from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ShipmentStatusChoices(models.TextChoices):
    BOOKED = 'BOOKED', 'Booked'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    PICKUP_READY = 'PICKUP_READY', 'Pickup Ready'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    CUSTOMS_PROCESSING = 'CUSTOMS_PROCESSING', 'Customs Processing'
    CUSTOMS_CLEARED = 'CUSTOMS_CLEARED', 'Customs Cleared'
    DELIVERED = 'DELIVERED', 'Delivered'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    FAILED = 'FAILED', 'Failed'
    DISPUTED = 'DISPUTED', 'Disputed'


class Shipment(BaseModel):
    load = models.OneToOneField(
        'marketplace.Load',
        on_delete=models.CASCADE,
        related_name='shipment',
        db_index=True
    )
    bid = models.OneToOneField(
        'marketplace.Bid',
        on_delete=models.CASCADE,
        related_name='shipment',
        db_index=True
    )
    shipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipper_shipments',
        db_index=True
    )
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transporter_shipments',
        db_index=True
    )
    vehicle = models.ForeignKey(
        'fleet.Vehicle',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shipments'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='driver_shipments'
    )
    status = models.CharField(
        max_length=30,
        choices=ShipmentStatusChoices.choices,
        default=ShipmentStatusChoices.BOOKED,
        db_index=True
    )

    # Lifecycle Timestamps
    assigned_at = models.DateTimeField(null=True, blank=True)
    pickup_ready_at = models.DateTimeField(null=True, blank=True)
    departed_at = models.DateTimeField(null=True, blank=True)
    customs_processing_at = models.DateTimeField(null=True, blank=True)
    customs_cleared_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    # Cancellation metadata
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cancelled_shipments'
    )

    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['transporter', 'status']),
            models.Index(fields=['shipper', 'status']),
            models.Index(fields=['driver', 'status']),
        ]

    def __str__(self):
        return f"Shipment #{self.id} [Load {self.load_id}] - {self.status}"
