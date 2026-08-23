from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel
from .risk_zone import RiskSeverityChoices

class IncidentTypeChoices(models.TextChoices):
    ACCIDENT = 'ACCIDENT', 'Traffic / Vehicle Accident'
    CHECKPOINT_DELAY = 'CHECKPOINT_DELAY', 'Customs / Security Checkpoint Delay'
    FUEL_UNAVAILABLE = 'FUEL_UNAVAILABLE', 'Fuel Shortage / Station Outage'
    ROAD_PROBLEM = 'ROAD_PROBLEM', 'Road Damage / Blockage'
    SECURITY_INCIDENT = 'SECURITY_INCIDENT', 'Security Threat / Conflict Incident'


class IncidentStatusChoices(models.TextChoices):
    REPORTED = 'REPORTED', 'Reported'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    VERIFIED = 'VERIFIED', 'Verified'
    RESOLVED = 'RESOLVED', 'Resolved'
    DISMISSED = 'DISMISSED', 'Dismissed'


class IncidentReport(BaseModel):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_incidents')
    shipment = models.ForeignKey('shipments.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_incidents')
    incident_type = models.CharField(max_length=30, choices=IncidentTypeChoices.choices)
    description = models.TextField()
    location = models.PointField(srid=4326, geography=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    reported_at = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=20, choices=RiskSeverityChoices.choices, default=RiskSeverityChoices.MEDIUM)
    status = models.CharField(max_length=20, choices=IncidentStatusChoices.choices, default=IncidentStatusChoices.REPORTED, db_index=True)
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_incidents')

    class Meta:
        verbose_name = 'Incident Report'
        verbose_name_plural = 'Incident Reports'
        ordering = ['-reported_at']

    def __str__(self):
        return f"Incident: {self.get_incident_type_display()} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.location and self.latitude is not None and self.longitude is not None:
            from django.contrib.gis.geos import Point
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)
