from rest_framework import serializers
from apps.profiles.models import DriverProfile
from apps.accounts.models import User

class DriverProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    transporter_name = serializers.CharField(source='transporter.business_name', read_only=True)

    class Meta:
        model = DriverProfile
        fields = (
            'id', 'user', 'transporter', 'transporter_name', 'license_number',
            'license_type', 'license_expiry_date', 'emergency_contact_name',
            'emergency_contact_phone', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'transporter', 'created_at', 'updated_at')
