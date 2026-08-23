from decimal import Decimal
from rest_framework import serializers
from apps.risk.models import RiskZone, RiskSeverityChoices, RiskZoneSourceChoices

class RiskZoneSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True, default=None)
    is_currently_effective = serializers.BooleanField(read_only=True)

    class Meta:
        model = RiskZone
        fields = (
            'id',
            'name',
            'description',
            'latitude',
            'longitude',
            'radius_km',
            'severity',
            'source',
            'is_active',
            'effective_from',
            'effective_until',
            'created_by_email',
            'verified_at',
            'is_currently_effective',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by_email', 'verified_at', 'is_currently_effective', 'created_at', 'updated_at')


class CreateRiskZoneSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-90.0'), max_value=Decimal('90.0'))
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=Decimal('-180.0'), max_value=Decimal('180.0'))
    radius_km = serializers.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'), min_value=Decimal('0.10'))
    severity = serializers.ChoiceField(choices=RiskSeverityChoices.choices, default=RiskSeverityChoices.HIGH)
    source = serializers.ChoiceField(choices=RiskZoneSourceChoices.choices, default=RiskZoneSourceChoices.ADMIN)
    effective_from = serializers.DateTimeField(required=False, allow_null=True)
    effective_until = serializers.DateTimeField(required=False, allow_null=True)
