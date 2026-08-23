from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class Commission(BaseModel):
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='commission',
        db_index=True
    )
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'), help_text="Commission rate percentage e.g. 5.00%")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    calculation_version = models.CharField(max_length=30, default='v1')
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'

    def __str__(self):
        return f"Commission for Payment #{self.payment_id}: {self.commission_amount} ETB ({self.rate}%)"
