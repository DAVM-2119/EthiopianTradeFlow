from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class DisputeStatusChoices(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    RESOLVED = 'RESOLVED', 'Resolved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'


class DisputeReasonChoices(models.TextChoices):
    AMOUNT_MISMATCH = 'AMOUNT_MISMATCH', 'Amount Mismatch'
    PAYMENT_NOT_RECEIVED = 'PAYMENT_NOT_RECEIVED', 'Payment Not Received'
    DUPLICATE_PAYMENT = 'DUPLICATE_PAYMENT', 'Duplicate Payment'
    PAYOUT_NOT_RECEIVED = 'PAYOUT_NOT_RECEIVED', 'Payout Not Received'
    PROVIDER_ERROR = 'PROVIDER_ERROR', 'Provider Error'
    OTHER = 'OTHER', 'Other'


class PaymentDispute(BaseModel):
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='disputes',
        db_index=True
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disputes_raised',
        db_index=True
    )
    reason = models.CharField(
        max_length=30,
        choices=DisputeReasonChoices.choices,
        default=DisputeReasonChoices.OTHER
    )
    description = models.TextField()
    disputed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=DisputeStatusChoices.choices,
        default=DisputeStatusChoices.OPEN,
        db_index=True
    )
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='disputes_resolved'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payment Dispute'
        verbose_name_plural = 'Payment Disputes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute #{self.id} for Payment #{self.payment_id} [{self.reason}] - {self.status}"
