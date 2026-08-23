from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.verification.models import Verification
from apps.verification.serializers.history import VerificationHistorySerializer
from apps.accounts.serializers import UserSerializer
from apps.profiles.services import get_or_create_user_profile
from apps.fleet.serializers import VehicleSerializer
from apps.fleet.models import Vehicle

class VerificationSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = Verification
        fields = (
            'id', 'user', 'user_email', 'user_role', 'status',
            'submitted_at', 'verified_at', 'suspended_at', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class VerificationActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class AdminVerificationDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()
    history = VerificationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Verification
        fields = (
            'id', 'user', 'status', 'submitted_at', 'verified_at',
            'suspended_at', 'profile', 'vehicles', 'history', 'created_at', 'updated_at'
        )
        read_only_fields = fields

    @extend_schema_field(serializers.DictField(required=False, allow_null=True))
    def get_profile(self, obj):
        try:
            profile_obj, serializer_class = get_or_create_user_profile(obj.user)
            return serializer_class(profile_obj).data
        except Exception:
            return None

    @extend_schema_field(VehicleSerializer(many=True))
    def get_vehicles(self, obj):
        if hasattr(obj.user, 'transporter_profile'):
            vehicles = Vehicle.objects.filter(transporter=obj.user.transporter_profile).prefetch_related('documents')
            return VehicleSerializer(vehicles, many=True).data
        return []
