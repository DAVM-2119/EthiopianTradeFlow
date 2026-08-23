from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ContractRate(BaseModel):
    """
    Locked contract pricing rate agreed between a shipper and a transporter or platform.
    FR-04.2 Contract-rate shippers lock rates for a defined validity window.
    """
    shipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contract_rates',
        db_index=True
    )
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='transporter_contract_rates'
    )
    origin_city = models.CharField(max_length=100, db_index=True)
    destination_city = models.CharField(max_length=100, db_index=True)
    agreed_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Agreed locked freight rate in ETB"
    )
    currency = models.CharField(max_length=10, default='ETB')
    valid_from = models.DateTimeField(db_index=True)
    valid_until = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    divergence_threshold_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        help_text="Allowed spot rate divergence percentage before warning flag"
    )

    class Meta:
        verbose_name = 'Contract Rate'
        verbose_name_plural = 'Contract Rates'
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract Rate ({self.origin_city} -> {self.destination_city}): {self.agreed_rate} {self.currency}"
