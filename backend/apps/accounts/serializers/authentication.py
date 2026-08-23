from rest_framework import serializers
from apps.accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'role', 'status', 'is_verified', 'is_active', 'is_staff',
            'created_at', 'updated_at'
        )
        read_only_fields = fields


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
