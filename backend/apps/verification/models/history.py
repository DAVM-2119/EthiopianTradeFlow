from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.verification.models.verification import VerificationStatusChoices

class VerificationHistory(BaseModel):
    verification = models.ForeignKey(
        'verification.Verification',
        on_delete=models.CASCADE,
        related_name='history',
        db_index=True
    )
    previous_status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices
    )
    new_status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verification_actions'
    )
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Verification History'
        verbose_name_plural = 'Verification Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"History #{self.id}: {self.previous_status} -> {self.new_status} by {self.changed_by}"
