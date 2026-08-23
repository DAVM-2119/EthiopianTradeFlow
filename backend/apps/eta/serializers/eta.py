from rest_framework import serializers
from apps.eta.models import ETAPrediction

class ETAPredictionSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)

    class Meta:
        model = ETAPrediction
        fields = (
            'id',
            'shipment_id',
            'predicted_at',
            'estimated_arrival',
            'remaining_distance_km',
            'expected_speed_kmh',
            'delay_minutes',
            'prediction_method',
            'algorithm_version',
            'confidence',
            'created_at',
        )
        read_only_fields = fields
