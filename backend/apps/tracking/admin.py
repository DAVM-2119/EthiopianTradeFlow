from django.contrib import admin
from apps.tracking.models import TrackingEvent

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'driver', 'latitude', 'longitude', 'speed', 'heading', 'recorded_at', 'received_at')
    list_filter = ('recorded_at', 'received_at')
    search_fields = ('shipment__id', 'driver__email', 'event_id')
    readonly_fields = ('event_id', 'shipment', 'driver', 'location', 'latitude', 'longitude', 'speed', 'heading', 'recorded_at', 'received_at', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False
