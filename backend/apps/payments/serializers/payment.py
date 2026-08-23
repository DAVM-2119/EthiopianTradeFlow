from rest_framework import serializers
from apps.payments.models import Payment, PaymentTransaction, Commission

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'provider', 'transaction_id', 'status', 'request_reference', 'response_reference', 'raw_response', 'created_at')


class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = ('id', 'rate', 'gross_amount', 'commission_amount', 'net_amount', 'calculation_version', 'calculated_at')


class PaymentSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)
    payer_id = serializers.UUIDField(source='payer.id', read_only=True)
    payer_email = serializers.EmailField(source='payer.email', read_only=True)
    commission = CommissionSerializer(read_only=True)
    transactions = PaymentTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'shipment_id',
            'payer_id',
            'payer_email',
            'amount',
            'currency',
            'status',
            'payment_method',
            'provider',
            'provider_transaction_id',
            'idempotency_key',
            'initiated_at',
            'confirmed_at',
            'failed_at',
            'failure_reason',
            'commission',
            'transactions',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class CreatePaymentSerializer(serializers.Serializer):
    shipment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='ETB')
    payment_method = serializers.CharField(max_length=30, default='MOBILE_MONEY')
    provider = serializers.CharField(max_length=30, default='MOCK')
    idempotency_key = serializers.CharField(max_length=100, required=False, allow_blank=True)


class ConfirmPaymentSerializer(serializers.Serializer):
    provider_transaction_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
