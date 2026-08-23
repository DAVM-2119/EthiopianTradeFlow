from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.core.exceptions import ValidationException

class PaymentStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    INITIATED = 'INITIATED', 'Initiated'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'


class PaymentMethodChoices(models.TextChoices):
    MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
    CASH = 'CASH', 'Cash'


class PaymentProviderChoices(models.TextChoices):
    MOCK = 'MOCK', 'Mock Payment Provider'
    TELEBIRR = 'TELEBIRR', 'TeleBirr'
    CBE_BIRR = 'CBE_BIRR', 'CBE Birr'


class Payment(BaseModel):
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='payments',
        db_index=True
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made',
        db_index=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')

    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
        db_index=True
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.MOBILE_MONEY
    )
    provider = models.CharField(
        max_length=30,
        choices=PaymentProviderChoices.choices,
        default=PaymentProviderChoices.MOCK
    )
    provider_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="Transaction reference from external payment provider"
    )
    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique client idempotency key to prevent duplicate payments"
    )

    initiated_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shipment', 'status']),
            models.Index(fields=['payer', 'status']),
        ]

    def __str__(self):
        return f"Payment #{self.id} [{self.amount} {self.currency}] - {self.status}"

    def transition_to(self, new_status: str, save: bool = True):
        valid_transitions = {
            PaymentStatusChoices.PENDING: [PaymentStatusChoices.INITIATED, PaymentStatusChoices.COMPLETED, PaymentStatusChoices.CANCELLED, PaymentStatusChoices.FAILED],
            PaymentStatusChoices.INITIATED: [PaymentStatusChoices.PROCESSING, PaymentStatusChoices.COMPLETED, PaymentStatusChoices.FAILED, PaymentStatusChoices.CANCELLED],
            PaymentStatusChoices.PROCESSING: [PaymentStatusChoices.COMPLETED, PaymentStatusChoices.FAILED, PaymentStatusChoices.CANCELLED],
            PaymentStatusChoices.COMPLETED: [PaymentStatusChoices.REFUNDED],
            PaymentStatusChoices.FAILED: [PaymentStatusChoices.INITIATED],
            PaymentStatusChoices.CANCELLED: [],
            PaymentStatusChoices.REFUNDED: [],
        }

        allowed = valid_transitions.get(self.status, [])
        if new_status not in allowed:
            raise ValidationException(f"Invalid payment state transition from '{self.status}' to '{new_status}'. Allowed: {allowed}")

        self.status = new_status
        if save:
            self.save(update_fields=['status', 'updated_at'])
