from decimal import Decimal
from rest_framework import serializers
from apps.fleet.models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    capacity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    transporter_name = serializers.CharField(source='transporter.business_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'transporter', 'transporter_name', 'registration_number',
            'vehicle_type', 'capacity', 'capacity_unit', 'fuel_type',
            'model', 'manufacturer', 'year', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'transporter', 'created_at', 'updated_at')
