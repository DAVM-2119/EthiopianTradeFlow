from decimal import Decimal
from rest_framework import serializers
from apps.risk.models import IncidentReport, IncidentTypeChoices, IncidentStatusChoices, RiskSeverityChoices

class IncidentReportSerializer(serializers.ModelSerializer):
    reported_by_email = serializers.EmailField(source='reported_by.email', read_only=True)
    driver_email = serializers.EmailField(source='driver.email', read_only=True, default=None)
    verified_by_email = serializers.EmailField(source='verified_by.email', read_only=True, default=None)

    class Meta:
        model = IncidentReport
        fields = (
            'id',
            'reported_by_email',
            'shipment',
            'driver',
            'driver_email',
            'incident_type',
            'description',
            'latitude',
            'longitude',
            'reported_at',
            'severity',
            'status',
            'verification_notes',
            'verified_by_email',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'reported_by_email', 'driver_email', 'verified_by_email', 'reported_at', 'created_at', 'updated_at')


class ReportIncidentSerializer(serializers.Serializer):
    shipment_id = serializers.UUIDField(required=False, allow_null=True)
    incident_type = serializers.ChoiceField(choices=IncidentTypeChoices.choices)
    description = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-90.0'), max_value=Decimal('90.0'))
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-180.0'), max_value=Decimal('180.0'))
    severity = serializers.ChoiceField(choices=RiskSeverityChoices.choices, default=RiskSeverityChoices.MEDIUM)


class VerifyIncidentSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=IncidentStatusChoices.choices)
    verification_notes = serializers.CharField(required=False, allow_blank=True, default="")
