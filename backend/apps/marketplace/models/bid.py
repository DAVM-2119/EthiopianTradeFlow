from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel

class BidStatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
    EXPIRED = 'EXPIRED', 'Expired'


class Bid(BaseModel):
    load = models.ForeignKey(
        'marketplace.Load',
        on_delete=models.CASCADE,
        related_name='bids',
        db_index=True
    )
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids',
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Bid amount in local currency (ETB)"
    )
    currency = models.CharField(max_length=3, default='ETB')
    proposed_pickup_date = models.DateTimeField(null=True, blank=True)
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True, help_text="Notes or message from transporter")
    
    status = models.CharField(
        max_length=20,
        choices=BidStatusChoices.choices,
        default=BidStatusChoices.ACTIVE,
        db_index=True
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='bid_amount_positive_check'
            ),
            models.UniqueConstraint(
                fields=['load', 'transporter'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_bid_per_transporter_and_load'
            )
        ]
        indexes = [
            models.Index(fields=['load', 'status']),
            models.Index(fields=['transporter', 'status']),
            models.Index(fields=['load', 'transporter']),
        ]

    def clean(self):
        super().clean()
        if self.proposed_pickup_date and self.estimated_delivery_date:
            if self.proposed_pickup_date > self.estimated_delivery_date:
                raise ValidationError({"proposed_pickup_date": "Proposed pickup date cannot be after estimated delivery date."})

    def __str__(self):
        return f"Bid #{self.id} for Load {self.load_id} by {self.transporter.email} - {self.amount} {self.currency} [{self.status}]"
