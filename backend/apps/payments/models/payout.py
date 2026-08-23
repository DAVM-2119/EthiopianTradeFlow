from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class PayoutStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Payout(BaseModel):
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts',
        db_index=True
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='payouts',
        db_index=True
    )
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PayoutStatusChoices.choices,
        default=PayoutStatusChoices.PENDING,
        db_index=True
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payout #{self.id} to Transporter #{self.transporter_id}: {self.net_amount} ETB [{self.status}]"
