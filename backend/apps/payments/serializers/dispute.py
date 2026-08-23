from rest_framework import serializers
from apps.payments.models import PaymentDispute

class PaymentDisputeSerializer(serializers.ModelSerializer):
    payment_id = serializers.UUIDField(source='payment.id', read_only=True)
    raised_by_id = serializers.UUIDField(source='raised_by.id', read_only=True)
    raised_by_email = serializers.EmailField(source='raised_by.email', read_only=True)
    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)

    class Meta:
        model = PaymentDispute
        fields = (
            'id',
            'payment_id',
            'raised_by_id',
            'raised_by_email',
            'reason',
            'description',
            'disputed_amount',
            'status',
            'resolution_notes',
            'resolved_by_email',
            'resolved_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class RaiseDisputeSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=30)
    description = serializers.CharField()
    disputed_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class ResolveDisputeSerializer(serializers.Serializer):
    resolution_status = serializers.CharField(max_length=20)
    resolution_notes = serializers.CharField()
