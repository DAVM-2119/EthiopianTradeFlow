from rest_framework import serializers
from apps.notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_email', 'notification_type', 'title',
            'message', 'channel', 'status', 'priority', 'related_object_type',
            'related_object_id', 'data', 'idempotency_key', 'read', 'sent_at',
            'read_at', 'failure_reason', 'retry_count', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class CreateNotificationSerializer(serializers.Serializer):
    recipient_id = serializers.UUIDField()
    notification_type = serializers.CharField(max_length=40)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    channel = serializers.CharField(max_length=20, default='IN_APP')
    idempotency_key = serializers.CharField(max_length=150, required=False, allow_blank=True)
    priority = serializers.CharField(max_length=20, default='NORMAL')
    data = serializers.JSONField(required=False, default=dict)
    related_object_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    related_object_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
