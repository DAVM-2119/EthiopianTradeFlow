from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class SyncStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SYNCING = 'SYNCING', 'Syncing'
    SYNCED = 'SYNCED', 'Synced'
    FAILED = 'FAILED', 'Failed'
    CONFLICT = 'CONFLICT', 'Conflict'


class SyncEventTypeChoices(models.TextChoices):
    WAYPOINT_CHECKIN = 'WAYPOINT_CHECKIN', 'Waypoint Check-In'
    INCIDENT_REPORT = 'INCIDENT_REPORT', 'Incident Report'
    TRACKING_EVENT = 'TRACKING_EVENT', 'GPS Tracking Event'


class OfflineSyncEvent(BaseModel):
    """
    Append-only offline synchronization event model capturing driver actions performed offline.
    Guarantees idempotency via unique client_event_id per user.
    """
    client_event_id = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="Unique client-generated event UUID for idempotency"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offline_sync_events',
        db_index=True
    )
    device_id = models.CharField(max_length=255, blank=True, help_text="Identifier of mobile device")
    event_type = models.CharField(
        max_length=50,
        choices=SyncEventTypeChoices.choices,
        db_index=True
    )
    entity_type = models.CharField(max_length=50, blank=True, help_text="Target entity type, e.g. shipment")
    entity_id = models.UUIDField(null=True, blank=True, help_text="Target entity UUID, e.g. shipment_id")
    payload = models.JSONField(default=dict, help_text="Event payload data dictionary")
    
    client_created_at = models.DateTimeField(help_text="Timestamp when action was performed on device")
    client_updated_at = models.DateTimeField(null=True, blank=True)
    server_received_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=SyncStatusChoices.choices,
        default=SyncStatusChoices.PENDING,
        db_index=True
    )
    attempt_count = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    server_entity_id = models.CharField(max_length=255, blank=True, help_text="ID of server domain entity created/updated")

    class Meta:
        verbose_name = 'Offline Sync Event'
        verbose_name_plural = 'Offline Sync Events'
        ordering = ['-client_created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event_type', 'entity_id']),
        ]

    def __str__(self):
        return f"SyncEvent {self.client_event_id} ({self.event_type} - {self.status})"
