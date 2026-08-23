from rest_framework import serializers
from apps.profiles.models import TransporterProfile

class TransporterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransporterProfile
        fields = ('id', 'business_name', 'legal_name', 'trade_license_number', 'tax_id', 'address', 'city', 'region', 'country', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
