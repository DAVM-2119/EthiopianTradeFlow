from rest_framework import serializers
from decimal import Decimal
from apps.tracking.models import TrackingEvent

class TrackingEventIngestSerializer(serializers.Serializer):
    shipment = serializers.UUIDField(required=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    speed = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    heading = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    recorded_at = serializers.DateTimeField(required=True)
    event_id = serializers.CharField(max_length=128, required=False, allow_blank=True, allow_null=True)

    def validate_latitude(self, value):
        if value < Decimal('-90.000000') or value > Decimal('90.000000'):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if value < Decimal('-180.000000') or value > Decimal('180.000000'):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value

    def validate_speed(self, value):
        if value is not None and value < Decimal('0.00'):
            raise serializers.ValidationError("Speed cannot be negative.")
        return value

    def validate_heading(self, value):
        if value is not None and (value < Decimal('0.00') or value >= Decimal('360.00')):
            raise serializers.ValidationError("Heading must be in range [0, 360).")
        return value


class TrackingEventSerializer(serializers.ModelSerializer):
    driver_email = serializers.CharField(source='driver.email', read_only=True)

    class Meta:
        model = TrackingEvent
        fields = (
            'id', 'event_id', 'shipment', 'driver', 'driver_email',
            'latitude', 'longitude', 'speed', 'heading',
            'recorded_at', 'received_at'
        )
        read_only_fields = fields
