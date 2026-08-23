from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel
from .risk_zone import RiskSeverityChoices

class AlertTypeChoices(models.TextChoices):
    APPROACHING_RISK_ZONE = 'APPROACHING_RISK_ZONE', 'Approaching Risk Zone'
    INCIDENT_IN_PROXIMITY = 'INCIDENT_IN_PROXIMITY', 'Incident in Proximity'
    ROUTE_DEVIATION_RISK = 'ROUTE_DEVIATION_RISK', 'Route Deviation into Risk'


class AlertStatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
    RESOLVED = 'RESOLVED', 'Resolved'
    DISMISSED = 'DISMISSED', 'Dismissed'


class SecurityAlert(BaseModel):
    shipment = models.ForeignKey('shipments.Shipment', on_delete=models.CASCADE, related_name='security_alerts')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_alerts')
    risk_zone = models.ForeignKey('RiskZone', on_delete=models.SET_NULL, null=True, blank=True, related_name='security_alerts')
    incident = models.ForeignKey('IncidentReport', on_delete=models.SET_NULL, null=True, blank=True, related_name='security_alerts')
    alert_type = models.CharField(max_length=35, choices=AlertTypeChoices.choices)
    severity = models.CharField(max_length=20, choices=RiskSeverityChoices.choices, default=RiskSeverityChoices.HIGH)
    distance_at_detection_km = models.DecimalField(max_digits=8, decimal_places=2)
    message = models.TextField()
    suggested_action = models.TextField(blank=True)
    suggested_alternate_route_id = models.UUIDField(null=True, blank=True, help_text="Phase 16 Route candidate UUID integration boundary")
    status = models.CharField(max_length=20, choices=AlertStatusChoices.choices, default=AlertStatusChoices.ACTIVE, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')

    class Meta:
        verbose_name = 'Security Alert'
        verbose_name_plural = 'Security Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"SecurityAlert: {self.alert_type} for Shipment {self.shipment.id} ({self.status})"
