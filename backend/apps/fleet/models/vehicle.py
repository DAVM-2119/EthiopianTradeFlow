from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel

class VehicleTypeChoices(models.TextChoices):
    LIGHT_TRUCK = 'LIGHT_TRUCK', 'Light Truck'
    MEDIUM_TRUCK = 'MEDIUM_TRUCK', 'Medium Truck'
    HEAVY_TRUCK = 'HEAVY_TRUCK', 'Heavy Truck'
    TRACTOR_TRUCK = 'TRACTOR_TRUCK', 'Tractor Truck'
    TRAILER = 'TRAILER', 'Trailer'
    TANKER = 'TANKER', 'Tanker'
    REFRIGERATED_TRUCK = 'REFRIGERATED_TRUCK', 'Refrigerated Truck'
    OTHER = 'OTHER', 'Other'


class CapacityUnitChoices(models.TextChoices):
    TON = 'TON', 'Ton'
    KG = 'KG', 'Kilogram'
    CBM = 'CBM', 'Cubic Meter'


class FuelTypeChoices(models.TextChoices):
    DIESEL = 'DIESEL', 'Diesel'
    PETROL = 'PETROL', 'Petrol'
    ELECTRIC = 'ELECTRIC', 'Electric'
    HYBRID = 'HYBRID', 'Hybrid'
    OTHER = 'OTHER', 'Other'


class VehicleStatusChoices(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    IN_MAINTENANCE = 'IN_MAINTENANCE', 'In Maintenance'
    INACTIVE = 'INACTIVE', 'Inactive'


class Vehicle(BaseModel):
    transporter = models.ForeignKey(
        'profiles.TransporterProfile',
        on_delete=models.CASCADE,
        related_name='vehicles',
        db_index=True
    )
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Vehicle license plate / registration number'
    )
    vehicle_type = models.CharField(
        max_length=30,
        choices=VehicleTypeChoices.choices,
        default=VehicleTypeChoices.HEAVY_TRUCK,
        db_index=True
    )
    capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Maximum carrying payload capacity'
    )
    capacity_unit = models.CharField(
        max_length=10,
        choices=CapacityUnitChoices.choices,
        default=CapacityUnitChoices.TON
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelTypeChoices.choices,
        default=FuelTypeChoices.DIESEL,
        db_index=True
    )
    model = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=VehicleStatusChoices.choices,
        default=VehicleStatusChoices.AVAILABLE,
        db_index=True
    )

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name='vehicle_capacity_positive_check'
            )
        ]
        indexes = [
            models.Index(fields=['transporter', 'status']),
            models.Index(fields=['vehicle_type', 'status']),
        ]

    def __str__(self):
        return f"{self.registration_number} ({self.vehicle_type} - {self.capacity} {self.capacity_unit})"
