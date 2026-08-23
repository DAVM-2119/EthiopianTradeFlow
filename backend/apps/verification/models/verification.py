from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class VerificationStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending Review'
    VERIFIED = 'VERIFIED', 'Verified'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    REJECTED = 'REJECTED', 'Rejected'


class Verification(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.PENDING,
        db_index=True
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Verification'
        verbose_name_plural = 'Verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
        ]

    def __str__(self):
        return f"Verification ({self.user.email}) - Status: {self.status}"
