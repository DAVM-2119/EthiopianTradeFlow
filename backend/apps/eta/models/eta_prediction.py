from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class ETAPrediction(BaseModel):
    """
    Persisted ETA prediction record for an active shipment.
    Records predicted arrival timestamp, remaining distance, speed assumptions, and delay inputs.
    """
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='eta_predictions',
        db_index=True
    )
    predicted_at = models.DateTimeField(db_index=True, help_text="Timestamp when calculation was performed")
    estimated_arrival = models.DateTimeField(db_index=True, help_text="Predicted arrival date & time")
    
    remaining_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated remaining distance in kilometers"
    )
    expected_speed_kmh = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Expected vehicle travel speed in km/h"
    )
    delay_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Total accumulated delay in minutes (check-ins, incidents, checkpoints)"
    )
    
    prediction_method = models.CharField(
        max_length=50,
        default='RULE_BASED',
        db_index=True,
        help_text="Method tag: RULE_BASED, ML, etc."
    )
    algorithm_version = models.CharField(
        max_length=50,
        default='eta-v1',
        help_text="Algorithm identifier version"
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.85'),
        help_text="Prediction confidence score between 0.00 and 1.00"
    )

    class Meta:
        verbose_name = 'ETA Prediction'
        verbose_name_plural = 'ETA Predictions'
        ordering = ['-predicted_at']
        indexes = [
            models.Index(fields=['shipment', '-predicted_at']),
        ]

    def __str__(self):
        return f"ETA for Shipment {self.shipment_id}: {self.estimated_arrival} (Dist: {self.remaining_distance_km} km)"
