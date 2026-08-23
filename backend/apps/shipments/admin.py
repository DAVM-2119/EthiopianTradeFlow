from django.contrib import admin
from apps.shipments.models import Shipment, ShipmentEvent, ProofOfDelivery

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'load', 'shipper', 'transporter', 'vehicle', 'driver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('load__title', 'shipper__email', 'transporter__email', 'driver__email')
    readonly_fields = (
        'load', 'bid', 'shipper', 'transporter', 'assigned_at',
        'pickup_ready_at', 'departed_at', 'customs_processing_at',
        'customs_cleared_at', 'delivered_at', 'completed_at',
        'cancelled_at', 'failed_at', 'cancelled_by', 'cancellation_reason',
        'created_at', 'updated_at'
    )


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'event_type', 'previous_status', 'new_status', 'created_by', 'created_at')
    list_filter = ('event_type', 'new_status')
    search_fields = ('shipment__id', 'description', 'created_by__email')
    readonly_fields = ('shipment', 'event_type', 'previous_status', 'new_status', 'description', 'created_by', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False


@admin.register(ProofOfDelivery)
class ProofOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'receiver_name', 'delivery_timestamp', 'submitted_by', 'created_at')
    search_fields = ('shipment__id', 'receiver_name', 'submitted_by__email')
    readonly_fields = ('shipment', 'submitted_by', 'created_at', 'updated_at')
