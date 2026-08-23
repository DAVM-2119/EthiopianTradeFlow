from rest_framework import serializers
from apps.notifications.models import NotificationPreference

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'user', 'notification_type', 'channel', 'enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UpdatePreferenceSerializer(serializers.Serializer):
    notification_type = serializers.CharField(max_length=40)
    channel = serializers.CharField(max_length=20)
    enabled = serializers.BooleanField()
