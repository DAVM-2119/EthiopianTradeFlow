from django.contrib.gis.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TrackingEvent(BaseModel):
    event_id = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional client/device unique identifier for duplicate event prevention foundation."
    )
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='tracking_events',
        db_index=True
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracking_events',
        db_index=True
    )
    location = models.PointField(
        srid=4326,
        geography=True,
        help_text="Spatial PostGIS WGS84 Point(longitude, latitude)."
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Geographic latitude value in range [-90, 90]."
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Geographic longitude value in range [-180, 180]."
    )
    speed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Speed in km/h."
    )
    heading = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Heading in degrees [0, 360)."
    )
    recorded_at = models.DateTimeField(
        db_index=True,
        help_text="Timestamp generated on the GPS device."
    )
    received_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the server received the event."
    )

    class Meta:
        verbose_name = 'Tracking Event'
        verbose_name_plural = 'Tracking Events'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['shipment', '-recorded_at']),
            models.Index(fields=['driver', '-recorded_at']),
            models.Index(fields=['-recorded_at']),
        ]

    def __str__(self):
        return f"TrackingEvent #{self.id} [Shipment {self.shipment_id}] at {self.recorded_at}"
