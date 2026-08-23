from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class PriceQuote(BaseModel):
    """
    Persisted spot price quote generated for a freight load.
    Records base price, demand multiplier, fuel multiplier, congestion multiplier,
    calculated price, final clamped price, and divergence warning notes.
    """
    load = models.ForeignKey(
        'marketplace.Load',
        on_delete=models.CASCADE,
        related_name='price_quotes',
        db_index=True
    )
    shipment = models.ForeignKey(
        'shipments.Shipment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='price_quotes'
    )
    
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Base rate calculation before dynamic adjustments"
    )
    demand_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Demand/capacity ratio multiplier"
    )
    fuel_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Fuel price index multiplier"
    )
    congestion_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Corridor congestion level multiplier"
    )
    calculated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price output before floor/ceiling clamping"
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Final price output after floor/ceiling bounds"
    )
    currency = models.CharField(max_length=10, default='ETB')
    
    pricing_method = models.CharField(
        max_length=50,
        default='RULE_BASED',
        db_index=True,
        help_text="Method tag: RULE_BASED, ML, etc."
    )
    algorithm_version = models.CharField(
        max_length=50,
        default='pricing-v1',
        help_text="Pricing algorithm version identifier"
    )
    
    valid_from = models.DateTimeField(db_index=True)
    valid_until = models.DateTimeField(db_index=True)
    
    divergence_warning = models.BooleanField(
        default=False,
        help_text="Flagged True if spot rate diverges significantly from locked contract rate"
    )
    divergence_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Price Quote'
        verbose_name_plural = 'Price Quotes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['load', '-created_at']),
        ]

    def __str__(self):
        return f"Price Quote for Load {self.load_id}: {self.final_price} {self.currency}"
