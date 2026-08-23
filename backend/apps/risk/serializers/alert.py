from decimal import Decimal
from rest_framework import serializers
from apps.risk.models import SecurityAlert, AlertTypeChoices, AlertStatusChoices, RiskSeverityChoices
from .risk import RiskZoneSerializer
from .incident import IncidentReportSerializer

class SecurityAlertSerializer(serializers.ModelSerializer):
    driver_email = serializers.EmailField(source='driver.email', read_only=True, default=None)
    acknowledged_by_email = serializers.EmailField(source='acknowledged_by.email', read_only=True, default=None)
    risk_zone_name = serializers.CharField(source='risk_zone.name', read_only=True, default=None)
    incident_type = serializers.CharField(source='incident.incident_type', read_only=True, default=None)

    class Meta:
        model = SecurityAlert
        fields = (
            'id',
            'shipment',
            'driver',
            'driver_email',
            'risk_zone',
            'risk_zone_name',
            'incident',
            'incident_type',
            'alert_type',
            'severity',
            'distance_at_detection_km',
            'message',
            'suggested_action',
            'suggested_alternate_route_id',
            'status',
            'created_at',
            'acknowledged_at',
            'acknowledged_by_email',
        )
        read_only_fields = fields


class CheckLocationRequestSerializer(serializers.Serializer):
    shipment_id = serializers.UUIDField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-90.0'), max_value=Decimal('90.0'))
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-180.0'), max_value=Decimal('180.0'))


class CheckLocationResponseSerializer(serializers.Serializer):
    shipment_id = serializers.UUIDField()
    checked_at = serializers.CharField()
    risk_detected = serializers.BooleanField()
    detected_zones = serializers.ListField()
    new_alerts_count = serializers.IntegerField()
    generated_alerts = SecurityAlertSerializer(many=True)
