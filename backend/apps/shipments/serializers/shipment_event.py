from rest_framework import serializers
from apps.shipments.models import ShipmentEvent

class ShipmentEventSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = ShipmentEvent
        fields = (
            'id', 'shipment', 'event_type', 'previous_status', 'new_status',
            'description', 'created_by_email', 'created_at'
        )
        read_only_fields = fields
