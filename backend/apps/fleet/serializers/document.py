from rest_framework import serializers
from apps.fleet.models import VehicleDocument

class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ('id', 'vehicle', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
