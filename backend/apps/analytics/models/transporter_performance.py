from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TransporterPerformance(BaseModel):
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        db_index=True
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    period = models.CharField(max_length=7, db_index=True, help_text="Format YYYY-MM")

    completed_trips = models.IntegerField(default=0)
    on_time_trips = models.IntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Percentage 0.00 - 100.00")

    incident_count = models.IntegerField(default=0)
    incident_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Percentage 0.00 - 100.00")

    total_distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_fuel_liters = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fuel_efficiency = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="km per Liter")

    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="1.00 - 5.00")
    rating_count = models.IntegerField(default=0)

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transporter Performance'
        verbose_name_plural = 'Transporter Performances'
        ordering = ['-year', '-month', 'transporter']
        constraints = [
            models.UniqueConstraint(fields=['transporter', 'year', 'month'], name='unique_transporter_monthly_performance')
        ]

    def __str__(self):
        return f"Performance: {self.transporter.email} [{self.period}]"
