from decimal import Decimal
from django.db import models
from apps.core.models import BaseModel

class SettlementStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    RECONCILED = 'RECONCILED', 'Reconciled'
    COMPLETED = 'COMPLETED', 'Completed'
    DISPUTED = 'DISPUTED', 'Disputed'


class Settlement(BaseModel):
    shipment = models.OneToOneField(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='settlement',
        db_index=True
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='settlements',
        db_index=True
    )
    commission = models.ForeignKey(
        'payments.Commission',
        on_delete=models.CASCADE,
        related_name='settlements'
    )
    payout = models.ForeignKey(
        'payments.Payout',
        on_delete=models.CASCADE,
        related_name='settlements'
    )
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_transporter_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=SettlementStatusChoices.choices,
        default=SettlementStatusChoices.PENDING,
        db_index=True
    )
    reconciled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Settlement'
        verbose_name_plural = 'Settlements'
        ordering = ['-created_at']

    def __str__(self):
        return f"Settlement #{self.id} for Shipment #{self.shipment_id} - {self.status}"
