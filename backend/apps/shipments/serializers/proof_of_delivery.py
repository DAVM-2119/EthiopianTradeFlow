from rest_framework import serializers
from apps.shipments.models import ProofOfDelivery

class ProofOfDeliverySerializer(serializers.ModelSerializer):
    submitted_by_email = serializers.CharField(source='submitted_by.email', read_only=True)

    class Meta:
        model = ProofOfDelivery
        fields = (
            'id', 'shipment', 'receiver_name', 'delivery_timestamp',
            'signature_reference', 'photo_reference', 'notes',
            'submitted_by_email', 'created_at'
        )
        read_only_fields = ('id', 'shipment', 'submitted_by_email', 'created_at')
