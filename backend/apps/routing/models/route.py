from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class RouteStatusChoices(models.TextChoices):
    ROUTE_ACTIVE = 'ROUTE_ACTIVE', 'Active Route'
    REROUTE_PROPOSED = 'REROUTE_PROPOSED', 'Reroute Proposed'
    REROUTE_ACCEPTED = 'REROUTE_ACCEPTED', 'Reroute Accepted'
    REROUTE_REJECTED = 'REROUTE_REJECTED', 'Reroute Rejected'
    INACTIVE = 'INACTIVE', 'Inactive / Historical'


class Route(BaseModel):
    """
    Persisted route candidate or active route for a shipment.
    Stores spatial distance, travel time, fuel consumption estimates, fuel cost,
    security risk scores, optimization scores, and rerouting status.
    """
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='routes',
        db_index=True
    )
    provider = models.CharField(
        max_length=50,
        default='OSRM',
        help_text="Routing provider: OSRM, Geodesic, etc."
    )
    provider_route_id = models.CharField(max_length=255, blank=True)
    
    origin_city = models.CharField(max_length=100, db_index=True)
    destination_city = models.CharField(max_length=100, db_index=True)
    
    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total route distance in kilometers"
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Estimated travel duration in minutes"
    )
    estimated_fuel_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated fuel consumption in liters"
    )
    estimated_fuel_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Estimated total fuel cost in ETB"
    )
    
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.10'),
        help_text="Security/corridor risk score between 0.00 (safe) and 1.00 (severe risk)"
    )
    optimization_score = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        help_text="Weighted multi-attribute cost score (lower is better)"
    )
    
    status = models.CharField(
        max_length=30,
        choices=RouteStatusChoices.choices,
        default=RouteStatusChoices.ROUTE_ACTIVE,
        db_index=True
    )
    is_recommended = models.BooleanField(default=False, db_index=True)
    algorithm_version = models.CharField(max_length=50, default='routing-v1')
    geometry_json = models.JSONField(default=dict, blank=True, help_text="GeoJSON or coordinate list representation")

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        ordering = ['optimization_score', '-created_at']
        indexes = [
            models.Index(fields=['shipment', 'status']),
            models.Index(fields=['shipment', 'is_recommended']),
        ]

    def __str__(self):
        return f"Route for Shipment {self.shipment_id}: {self.distance_km} km ({self.duration_minutes} min, Status: {self.status})"
