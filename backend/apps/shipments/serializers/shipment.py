from rest_framework import serializers
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.marketplace.serializers import LoadSerializer
from apps.fleet.serializers import VehicleSerializer
from apps.accounts.serializers import UserSerializer
from apps.shipments.serializers.proof_of_delivery import ProofOfDeliverySerializer

class ShipmentListSerializer(serializers.ModelSerializer):
    shipper_email = serializers.CharField(source='shipper.email', read_only=True)
    transporter_email = serializers.CharField(source='transporter.email', read_only=True)
    driver_email = serializers.CharField(source='driver.email', read_only=True, allow_null=True)
    load_title = serializers.CharField(source='load.title', read_only=True)
    origin_city = serializers.CharField(source='load.origin_city', read_only=True)
    destination_city = serializers.CharField(source='load.destination_city', read_only=True)

    class Meta:
        model = Shipment
        fields = (
            'id', 'load', 'load_title', 'origin_city', 'destination_city',
            'shipper', 'shipper_email', 'transporter', 'transporter_email',
            'vehicle', 'driver', 'driver_email', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class ShipmentDetailSerializer(serializers.ModelSerializer):
    load = LoadSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    shipper = UserSerializer(read_only=True)
    transporter = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    proof_of_delivery = ProofOfDeliverySerializer(read_only=True)

    class Meta:
        model = Shipment
        fields = (
            'id', 'load', 'bid', 'shipper', 'transporter', 'vehicle', 'driver',
            'status', 'assigned_at', 'pickup_ready_at', 'departed_at',
            'customs_processing_at', 'customs_cleared_at', 'delivered_at',
            'completed_at', 'cancelled_at', 'failed_at', 'cancellation_reason',
            'cancelled_by', 'proof_of_delivery', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class ShipmentAssignmentSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField(required=True)
    driver_id = serializers.UUIDField(required=True)


class ShipmentTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ShipmentStatusChoices.choices, required=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')


class ShipmentCancellationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, min_length=5)
