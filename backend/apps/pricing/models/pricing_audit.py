from django.db import models
from apps.core.models import BaseModel

class PricingAudit(BaseModel):
    """
    Audit log record for every price computation.
    FR-04.3 Every price computation is logged with its exact input values for complete auditability.
    """
    price_quote = models.ForeignKey(
        'pricing.PriceQuote',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_index=True
    )
    input_snapshot = models.JSONField(
        default=dict,
        help_text="Exact JSON snapshot of all calculation inputs (base_rate, demand, fuel, congestion, floor, ceiling)"
    )
    output_snapshot = models.JSONField(
        default=dict,
        help_text="Exact JSON snapshot of calculation results and multipliers"
    )
    algorithm_version = models.CharField(max_length=50)
    calculated_at = models.DateTimeField(auto_now_add=True, db_index=True)
    calculation_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Pricing Audit'
        verbose_name_plural = 'Pricing Audits'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"Audit for Quote {self.price_quote_id} at {self.calculated_at}"
