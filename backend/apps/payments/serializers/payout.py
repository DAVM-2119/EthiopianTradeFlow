from rest_framework import serializers
from apps.payments.models import Payout

class PayoutSerializer(serializers.ModelSerializer):
    transporter_id = serializers.UUIDField(source='transporter.id', read_only=True)
    transporter_email = serializers.EmailField(source='transporter.email', read_only=True)
    payment_id = serializers.UUIDField(source='payment.id', read_only=True)

    class Meta:
        model = Payout
        fields = (
            'id',
            'transporter_id',
            'transporter_email',
            'payment_id',
            'gross_amount',
            'commission_amount',
            'net_amount',
            'status',
            'scheduled_at',
            'processed_at',
            'provider_transaction_id',
            'failure_reason',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields
