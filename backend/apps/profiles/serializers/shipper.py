from rest_framework import serializers
from apps.profiles.models import ShipperProfile

class ShipperProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipperProfile
        fields = ('id', 'business_name', 'legal_name', 'trade_license_number', 'tax_id', 'address', 'city', 'region', 'country', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
