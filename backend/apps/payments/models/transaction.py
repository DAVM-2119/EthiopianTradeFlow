from django.db import models
from apps.core.models import BaseModel

class PaymentTransactionStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'


class PaymentTransaction(BaseModel):
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='transactions',
        db_index=True
    )
    provider = models.CharField(max_length=30)
    transaction_id = models.CharField(max_length=100, db_index=True)
    request_reference = models.CharField(max_length=100, blank=True)
    response_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PaymentTransactionStatusChoices.choices,
        default=PaymentTransactionStatusChoices.PENDING
    )
    raw_response = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction #{self.transaction_id} [{self.provider}] - {self.status}"
