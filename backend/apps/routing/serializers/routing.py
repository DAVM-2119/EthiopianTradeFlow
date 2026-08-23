from rest_framework import serializers
from apps.routing.models import Route, RouteLeg

class RouteLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteLeg
        fields = (
            'id',
            'sequence',
            'start_point',
            'end_point',
            'distance_km',
            'duration_minutes',
            'estimated_fuel_liters',
            'road_condition',
            'security_risk_score',
        )
        read_only_fields = fields


class RouteSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)
    legs = RouteLegSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = (
            'id',
            'shipment_id',
            'provider',
            'provider_route_id',
            'origin_city',
            'destination_city',
            'distance_km',
            'duration_minutes',
            'estimated_fuel_liters',
            'estimated_fuel_cost',
            'risk_score',
            'optimization_score',
            'status',
            'is_recommended',
            'algorithm_version',
            'geometry_json',
            'legs',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class RerouteActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['propose', 'confirm', 'reject'])
    new_risk_score = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
