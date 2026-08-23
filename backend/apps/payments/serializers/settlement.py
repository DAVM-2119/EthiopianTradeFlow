from rest_framework import serializers
from apps.payments.models import Settlement
from .payment import CommissionSerializer
from .payout import PayoutSerializer

class SettlementSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)
    payment_id = serializers.UUIDField(source='payment.id', read_only=True)
    commission = CommissionSerializer(read_only=True)
    payout = PayoutSerializer(read_only=True)

    class Meta:
        model = Settlement
        fields = (
            'id',
            'shipment_id',
            'payment_id',
            'commission',
            'payout',
            'gross_amount',
            'commission_amount',
            'net_transporter_amount',
            'status',
            'reconciled_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields
