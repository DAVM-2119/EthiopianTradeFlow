from rest_framework import serializers
from apps.profiles.models import CustomsStaffProfile

class CustomsStaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsStaffProfile
        fields = ('id', 'organization', 'staff_identifier', 'office_location', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
