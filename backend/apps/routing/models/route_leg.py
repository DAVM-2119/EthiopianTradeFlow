from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class RouteLeg(BaseModel):
    """
    Sequenced leg component of a route.
    Allows decomposing a long freight corridor into waypoint legs for granular fuel & risk analysis (FR-05.2).
    """
    route = models.ForeignKey(
        'routing.Route',
        on_delete=models.CASCADE,
        related_name='legs',
        db_index=True
    )
    sequence = models.PositiveIntegerField(help_text="Leg sequence number (1, 2, 3...)")
    start_point = models.CharField(max_length=255, help_text="Leg origin waypoint/city")
    end_point = models.CharField(max_length=255, help_text="Leg destination waypoint/city")
    
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    estimated_fuel_liters = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    road_condition = models.CharField(max_length=50, default='GOOD')
    security_risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.10'))

    class Meta:
        verbose_name = 'Route Leg'
        verbose_name_plural = 'Route Legs'
        ordering = ['route', 'sequence']
        unique_together = ('route', 'sequence')

    def __str__(self):
        return f"Leg {self.sequence} ({self.start_point} -> {self.end_point}) of Route {self.route_id}"
