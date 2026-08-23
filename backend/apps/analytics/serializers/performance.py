from rest_framework import serializers
from apps.analytics.models import TransporterPerformance

class TransporterPerformanceSerializer(serializers.ModelSerializer):
    transporter_id = serializers.UUIDField(source='transporter.id', read_only=True)
    transporter_email = serializers.EmailField(source='transporter.email', read_only=True)

    class Meta:
        model = TransporterPerformance
        fields = (
            'id',
            'transporter_id',
            'transporter_email',
            'year',
            'month',
            'period',
            'completed_trips',
            'on_time_trips',
            'on_time_delivery_rate',
            'incident_count',
            'incident_rate',
            'total_distance_km',
            'total_fuel_liters',
            'fuel_efficiency',
            'average_rating',
            'rating_count',
            'calculated_at',
        )
        read_only_fields = fields


class CorridorBenchmarkSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_transporters_benchmarked = serializers.IntegerField()
    on_time_delivery_rate = serializers.FloatField()
    incident_rate = serializers.FloatField()
    fuel_efficiency = serializers.FloatField(allow_null=True)
    average_rating = serializers.FloatField(allow_null=True)


class TransporterDashboardResponseSerializer(serializers.Serializer):
    performance = TransporterPerformanceSerializer()
    corridor_benchmark = CorridorBenchmarkSerializer()
