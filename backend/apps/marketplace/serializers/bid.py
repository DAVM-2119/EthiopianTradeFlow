from decimal import Decimal
from rest_framework import serializers
from apps.marketplace.models import Bid, BidStatusChoices

class BidSerializer(serializers.ModelSerializer):
    transporter_email = serializers.CharField(source='transporter.email', read_only=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))

    class Meta:
        model = Bid
        fields = (
            'id', 'load', 'transporter', 'transporter_email', 'amount', 'currency',
            'proposed_pickup_date', 'estimated_delivery_date', 'message', 'status',
            'expires_at', 'accepted_at', 'withdrawn_at', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'load', 'transporter', 'status', 'accepted_at', 'withdrawn_at', 'created_at', 'updated_at')

    def validate(self, attrs):
        pickup = attrs.get('proposed_pickup_date') or (self.instance.proposed_pickup_date if self.instance else None)
        delivery = attrs.get('estimated_delivery_date') or (self.instance.estimated_delivery_date if self.instance else None)
        if pickup and delivery and pickup > delivery:
            raise serializers.ValidationError({"proposed_pickup_date": "Proposed pickup date cannot be after estimated delivery date."})
        return attrs


class BidCreateSerializer(BidSerializer):
    class Meta(BidSerializer.Meta):
        read_only_fields = ('id', 'load', 'transporter', 'status', 'accepted_at', 'withdrawn_at', 'created_at', 'updated_at')


class BidUpdateSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'), required=False)

    class Meta:
        model = Bid
        fields = (
            'amount', 'proposed_pickup_date', 'estimated_delivery_date', 'message', 'expires_at'
        )
