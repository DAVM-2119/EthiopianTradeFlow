from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TransporterProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transporter_profile'
    )
    business_name = models.CharField(max_length=255, blank=True)
    legal_name = models.CharField(max_length=255, blank=True)
    trade_license_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Ethiopia')

    class Meta:
        verbose_name = 'Transporter Profile'
        verbose_name_plural = 'Transporter Profiles'

    def __str__(self):
        return f"Transporter: {self.business_name or self.user.email}"
