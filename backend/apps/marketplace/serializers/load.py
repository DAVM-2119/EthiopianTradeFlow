from decimal import Decimal
from rest_framework import serializers
from apps.marketplace.models import Load, LoadStatusChoices

class LoadSerializer(serializers.ModelSerializer):
    shipper_email = serializers.CharField(source='shipper.email', read_only=True)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    volume = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'), required=False, allow_null=True)

    class Meta:
        model = Load
        fields = (
            'id', 'shipper', 'shipper_email', 'title', 'origin_city', 'origin_address',
            'destination_city', 'destination_address', 'cargo_type', 'weight', 'volume',
            'pickup_window_start', 'pickup_window_end', 'delivery_window_start',
            'delivery_window_end', 'special_requirements', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'shipper', 'status', 'created_at', 'updated_at')

    def validate(self, attrs):
        pickup_start = attrs.get('pickup_window_start') or (self.instance.pickup_window_start if self.instance else None)
        pickup_end = attrs.get('pickup_window_end') or (self.instance.pickup_window_end if self.instance else None)
        if pickup_start and pickup_end and pickup_start > pickup_end:
            raise serializers.ValidationError({"pickup_window_start": "Pickup window start cannot be after pickup window end."})

        delivery_start = attrs.get('delivery_window_start') or (self.instance.delivery_window_start if self.instance else None)
        delivery_end = attrs.get('delivery_window_end') or (self.instance.delivery_window_end if self.instance else None)
        if delivery_start and delivery_end and delivery_start > delivery_end:
            raise serializers.ValidationError({"delivery_window_start": "Delivery window start cannot be after delivery window end."})

        return attrs


class LoadCreateSerializer(LoadSerializer):
    status = serializers.ChoiceField(choices=[LoadStatusChoices.DRAFT, LoadStatusChoices.POSTED], default=LoadStatusChoices.DRAFT)

    class Meta(LoadSerializer.Meta):
        read_only_fields = ('id', 'shipper', 'created_at', 'updated_at')
