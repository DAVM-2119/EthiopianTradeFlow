from rest_framework import serializers
from apps.synchronization.models import OfflineSyncEvent, SyncEventTypeChoices

class OfflineSyncEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineSyncEvent
        fields = (
            'id',
            'client_event_id',
            'user',
            'device_id',
            'event_type',
            'entity_type',
            'entity_id',
            'payload',
            'client_created_at',
            'client_updated_at',
            'server_received_at',
            'status',
            'attempt_count',
            'last_attempt_at',
            'synced_at',
            'error_code',
            'error_message',
            'server_entity_id',
        )
        read_only_fields = fields


class OfflineSyncEventCreateSerializer(serializers.Serializer):
    client_event_id = serializers.UUIDField(required=True)
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    event_type = serializers.ChoiceField(choices=SyncEventTypeChoices.choices, required=True)
    entity_type = serializers.CharField(max_length=50, required=False, allow_blank=True, default='shipment')
    entity_id = serializers.UUIDField(required=True)
    payload = serializers.JSONField(required=False, default=dict)
    client_created_at = serializers.DateTimeField(required=True)
    client_updated_at = serializers.DateTimeField(required=False, allow_null=True, default=None)


class BatchSyncEventSerializer(serializers.Serializer):
    events = serializers.ListField(
        child=OfflineSyncEventCreateSerializer(),
        allow_empty=False,
        required=True
    )


class SyncStatusSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    syncing = serializers.IntegerField()
    synced = serializers.IntegerField()
    failed = serializers.IntegerField()
    conflict = serializers.IntegerField()
