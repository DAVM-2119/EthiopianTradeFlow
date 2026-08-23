from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel

class FuelDataSourceChoices(models.TextChoices):
    MANUAL = 'MANUAL', 'Manual Driver/Dispatcher Entry'
    TELEMATICS = 'TELEMATICS', 'Vehicle Telematics Sensor'
    FUEL_STATION = 'FUEL_STATION', 'Fuel Station Refueling Record'
    IMPORTED = 'IMPORTED', 'Imported Batch Log'
    CALCULATED = 'CALCULATED', 'System Calculated Baseline'


class TripFuelRecord(BaseModel):
    """
    Trip / Shipment Fuel Consumption Record (FR-07.1).
    Stores estimated vs. actual fuel consumption, distance, calculated efficiency (km/L),
    and variance metrics.
    """
    shipment = models.OneToOneField(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='fuel_record',
        db_index=True
    )
    vehicle = models.ForeignKey(
        'fleet.Vehicle',
        on_delete=models.CASCADE,
        related_name='fuel_records',
        db_index=True
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_fuel_records',
        db_index=True
    )
    
    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Trip distance in kilometers"
    )
    estimated_fuel_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated fuel consumption in liters"
    )
    actual_fuel_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual fuel consumption in liters (NULL if telematics/refueling data unavailable)"
    )
    
    fuel_efficiency_km_per_liter = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated fuel efficiency in km per liter"
    )
    fuel_variance_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual fuel minus estimated fuel in liters"
    )
    fuel_variance_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage variance: ((Actual - Estimated) / Estimated) * 100"
    )
    
    data_source = models.CharField(
        max_length=30,
        choices=FuelDataSourceChoices.choices,
        default=FuelDataSourceChoices.MANUAL
    )
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Trip Fuel Record'
        verbose_name_plural = 'Trip Fuel Records'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['vehicle', 'recorded_at']),
            models.Index(fields=['driver', 'recorded_at']),
        ]

    def __str__(self):
        return f"Fuel Record for Shipment {self.shipment_id} ({self.distance_km}km)"
