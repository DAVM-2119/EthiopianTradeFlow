from decimal import Decimal
from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel

class RiskSeverityChoices(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'


class RiskZoneSourceChoices(models.TextChoices):
    GOVERNMENT_ADVISORY = 'GOVERNMENT_ADVISORY', 'Government Advisory'
    VERIFIED_CROWDSOURCE = 'VERIFIED_CROWDSOURCE', 'Verified Crowdsource'
    ADMIN = 'ADMIN', 'Admin Flagged'


class RiskZone(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.PointField(srid=4326, geography=True, null=True, blank=True, help_text="Center spatial point WGS84")
    polygon = models.PolygonField(srid=4326, geography=True, null=True, blank=True, help_text="Spatial boundary polygon WGS84")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_km = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'), help_text="Alert threshold radius in kilometers")
    severity = models.CharField(max_length=20, choices=RiskSeverityChoices.choices, default=RiskSeverityChoices.HIGH)
    source = models.CharField(max_length=30, choices=RiskZoneSourceChoices.choices, default=RiskZoneSourceChoices.ADMIN)
    is_active = models.BooleanField(default=True, db_index=True)
    effective_from = models.DateTimeField(default=timezone.now)
    effective_until = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_risk_zones')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Risk Zone'
        verbose_name_plural = 'Risk Zones'
        ordering = ['-created_at']

    def __str__(self):
        return f"RiskZone: {self.name} ({self.severity})"

    def save(self, *args, **kwargs):
        if not self.location and self.latitude is not None and self.longitude is not None:
            from django.contrib.gis.geos import Point
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)

    @property
    def is_currently_effective(self) -> bool:
        now = timezone.now()
        if not self.is_active:
            return False
        if self.effective_from > now:
            return False
        if self.effective_until and self.effective_until < now:
            return False
        return True
