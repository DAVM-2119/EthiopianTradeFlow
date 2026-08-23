from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel

class MatchRecommendation(BaseModel):
    load = models.ForeignKey(
        'marketplace.Load',
        on_delete=models.CASCADE,
        related_name='match_recommendations',
        db_index=True
    )
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='match_recommendations',
        db_index=True
    )
    rank = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Rank order in shortlist (1=top match)")
    
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Weighted total match score (0.00 - 100.00)"
    )
    cost_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('75.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    reliability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('80.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    fuel_efficiency_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('70.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    proximity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('75.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    availability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    explanation = models.TextField(blank=True, help_text="Explainable breakdown of factors contributing to recommendation")
    algorithm_version = models.CharField(max_length=20, default='v1', help_text="Matching engine version tag")
    generated_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True, help_text="Whether recommendation is part of active shortlist")

    class Meta:
        verbose_name = 'Match Recommendation'
        verbose_name_plural = 'Match Recommendations'
        ordering = ['rank']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rank__gt=0),
                name='match_rank_positive_check'
            ),
            models.CheckConstraint(
                condition=models.Q(total_score__gte=0) & models.Q(total_score__lte=100),
                name='match_total_score_range_check'
            ),
            models.UniqueConstraint(
                fields=['load', 'transporter'],
                condition=models.Q(is_active=True),
                name='unique_active_match_recommendation_per_transporter_and_load'
            )
        ]
        indexes = [
            models.Index(fields=['load', 'is_active', 'rank']),
            models.Index(fields=['transporter', 'is_active']),
        ]

    def __str__(self):
        return f"Match #{self.rank} for Load {self.load_id} -> {self.transporter.email} (Score: {self.total_score})"
