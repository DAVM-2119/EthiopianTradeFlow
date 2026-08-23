from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel

class LoadStatusChoices(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    POSTED = 'POSTED', 'Posted'
    BOOKED = 'BOOKED', 'Booked'
    CANCELLED = 'CANCELLED', 'Cancelled'


class CargoTypeChoices(models.TextChoices):
    GENERAL_CARGO = 'GENERAL_CARGO', 'General Cargo'
    DRY_BULK = 'DRY_BULK', 'Dry Bulk'
    LIQUID_BULK = 'LIQUID_BULK', 'Liquid Bulk'
    CONTAINERIZED = 'CONTAINERIZED', 'Containerized'
    REFRIGERATED = 'REFRIGERATED', 'Refrigerated / Perishable'
    HAZARDOUS = 'HAZARDOUS', 'Hazardous Material'
    HEAVY_MACHINERY = 'HEAVY_MACHINERY', 'Heavy Machinery / Out of Gauge'


class Load(BaseModel):
    shipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loads',
        db_index=True
    )
    title = models.CharField(max_length=255, help_text="Short summary title of the freight load")
    origin_city = models.CharField(max_length=100, db_index=True, help_text="Origin city (e.g., Djibouti Port, Modjo, Addis Ababa)")
    origin_address = models.TextField(blank=True, help_text="Detailed pickup location address")
    destination_city = models.CharField(max_length=100, db_index=True, help_text="Destination city (e.g., Hawassa, Mekelle, Dire Dawa)")
    destination_address = models.TextField(blank=True, help_text="Detailed delivery location address")
    
    cargo_type = models.CharField(
        max_length=50,
        choices=CargoTypeChoices.choices,
        default=CargoTypeChoices.GENERAL_CARGO,
        db_index=True
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Weight in metric tons"
    )
    volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Volume in cubic meters"
    )
    
    pickup_window_start = models.DateTimeField(db_index=True, help_text="Earliest pickup date & time")
    pickup_window_end = models.DateTimeField(help_text="Latest pickup date & time")
    delivery_window_start = models.DateTimeField(null=True, blank=True, help_text="Earliest delivery date & time")
    delivery_window_end = models.DateTimeField(null=True, blank=True, help_text="Latest delivery date & time")
    
    special_requirements = models.TextField(blank=True, help_text="Temperature control, tarpaulin, handling instructions, etc.")
    status = models.CharField(
        max_length=20,
        choices=LoadStatusChoices.choices,
        default=LoadStatusChoices.DRAFT,
        db_index=True
    )

    class Meta:
        verbose_name = 'Load'
        verbose_name_plural = 'Loads'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight__gt=0),
                name='load_weight_positive_check'
            ),
            models.CheckConstraint(
                condition=models.Q(volume__isnull=True) | models.Q(volume__gt=0),
                name='load_volume_positive_check'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'origin_city', 'destination_city', 'cargo_type']),
            models.Index(fields=['shipper', 'status']),
        ]

    def clean(self):
        super().clean()
        if self.pickup_window_start and self.pickup_window_end:
            if self.pickup_window_start > self.pickup_window_end:
                raise ValidationError({"pickup_window_start": "Pickup window start cannot be after pickup window end."})
        if self.delivery_window_start and self.delivery_window_end:
            if self.delivery_window_start > self.delivery_window_end:
                raise ValidationError({"delivery_window_start": "Delivery window start cannot be after delivery window end."})

    def __str__(self):
        return f"Load [{self.title}] ({self.origin_city} -> {self.destination_city}) - {self.status}"
