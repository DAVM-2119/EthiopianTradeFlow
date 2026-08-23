from django.contrib import admin
from .models import OfflineSyncEvent

@admin.register(OfflineSyncEvent)
class OfflineSyncEventAdmin(admin.ModelAdmin):
    list_display = ('client_event_id', 'user', 'event_type', 'entity_type', 'status', 'client_created_at', 'synced_at')
    list_filter = ('status', 'event_type', 'entity_type')
    search_fields = ('client_event_id', 'user__email', 'device_id')
    readonly_fields = ('client_event_id', 'server_received_at', 'synced_at')
