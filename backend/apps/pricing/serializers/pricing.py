from rest_framework import serializers
from apps.pricing.models import PriceQuote, ContractRate, PricingAudit

class PricingAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingAudit
        fields = (
            'id',
            'input_snapshot',
            'output_snapshot',
            'algorithm_version',
            'calculated_at',
            'calculation_reason',
        )
        read_only_fields = fields


class PriceQuoteSerializer(serializers.ModelSerializer):
    load_id = serializers.UUIDField(source='load.id', read_only=True)
    audit_logs = PricingAuditSerializer(many=True, read_only=True)

    class Meta:
        model = PriceQuote
        fields = (
            'id',
            'load_id',
            'base_price',
            'demand_multiplier',
            'fuel_multiplier',
            'congestion_multiplier',
            'calculated_price',
            'final_price',
            'currency',
            'pricing_method',
            'algorithm_version',
            'valid_from',
            'valid_until',
            'divergence_warning',
            'divergence_notes',
            'audit_logs',
            'created_at',
        )
        read_only_fields = fields


class ContractRateSerializer(serializers.ModelSerializer):
    shipper_id = serializers.UUIDField(source='shipper.id', read_only=True)

    class Meta:
        model = ContractRate
        fields = (
            'id',
            'shipper_id',
            'transporter',
            'origin_city',
            'destination_city',
            'agreed_rate',
            'currency',
            'valid_from',
            'valid_until',
            'is_active',
            'divergence_threshold_percent',
            'created_at',
        )
        read_only_fields = ('id', 'shipper_id', 'created_at')
