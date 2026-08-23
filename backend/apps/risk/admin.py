from django.contrib import admin
from .models import RiskZone, IncidentReport, SecurityAlert

@admin.register(RiskZone)
class RiskZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'source', 'is_active', 'effective_from', 'effective_until')
    list_filter = ('severity', 'source', 'is_active')
    search_fields = ('name', 'description')


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('incident_type', 'severity', 'status', 'reported_by', 'shipment', 'reported_at')
    list_filter = ('incident_type', 'severity', 'status')
    search_fields = ('description', 'reported_by__email')


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'severity', 'status', 'shipment', 'driver', 'distance_at_detection_km', 'created_at')
    list_filter = ('alert_type', 'severity', 'status')
    search_fields = ('message', 'shipment__id')
