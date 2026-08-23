from decimal import Decimal
from rest_framework import serializers
from apps.analytics.models import TripFuelRecord, FuelDataSourceChoices

class TripFuelRecordSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)
    vehicle_id = serializers.UUIDField(source='vehicle.id', read_only=True)
    driver_id = serializers.UUIDField(source='driver.id', read_only=True, default=None)
    driver_email = serializers.EmailField(source='driver.email', read_only=True, default=None)

    class Meta:
        model = TripFuelRecord
        fields = (
            'id',
            'shipment_id',
            'vehicle_id',
            'driver_id',
            'driver_email',
            'distance_km',
            'estimated_fuel_liters',
            'actual_fuel_liters',
            'fuel_efficiency_km_per_liter',
            'fuel_variance_liters',
            'fuel_variance_percentage',
            'data_source',
            'recorded_at',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class RecordTripFuelSerializer(serializers.Serializer):
    actual_fuel_liters = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    distance_km = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    estimated_fuel_liters = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2, min_value=Decimal('0.00'))
    data_source = serializers.ChoiceField(choices=FuelDataSourceChoices.choices, default=FuelDataSourceChoices.MANUAL)
    notes = serializers.CharField(required=False, allow_blank=True)


class VehicleFuelMetricsSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    total_trips = serializers.IntegerField()
    total_distance_km = serializers.FloatField()
    total_estimated_fuel_liters = serializers.FloatField()
    total_actual_fuel_liters = serializers.FloatField()
    average_fuel_efficiency_km_per_liter = serializers.FloatField()
    average_variance_percentage = serializers.FloatField()


class DriverFuelMetricsSerializer(serializers.Serializer):
    driver_id = serializers.UUIDField()
    total_trips = serializers.IntegerField()
    total_distance_km = serializers.FloatField()
    total_estimated_fuel_liters = serializers.FloatField()
    total_actual_fuel_liters = serializers.FloatField()
    average_fuel_efficiency_km_per_liter = serializers.FloatField()
    average_variance_percentage = serializers.FloatField()


class FuelTrendSerializer(serializers.Serializer):
    period = serializers.CharField()
    trip_count = serializers.IntegerField()
    total_distance_km = serializers.FloatField()
    total_estimated_fuel_liters = serializers.FloatField()
    total_actual_fuel_liters = serializers.FloatField()
    average_efficiency_km_per_liter = serializers.FloatField()
    average_variance_percentage = serializers.FloatField()


class FuelRecommendationSerializer(serializers.Serializer):
    category = serializers.CharField()
    title = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    actionable_advice = serializers.CharField()
    metadata = serializers.DictField()
