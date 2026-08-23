from django.contrib import admin
from apps.fleet.models import Vehicle, VehicleDocument

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'transporter', 'vehicle_type', 'capacity', 'capacity_unit', 'fuel_type', 'status', 'created_at')
    list_filter = ('vehicle_type', 'fuel_type', 'status', 'capacity_unit')
    search_fields = ('registration_number', 'transporter__business_name', 'transporter__user__email')


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'document_type', 'document_number', 'status', 'expiry_date')
    list_filter = ('document_type', 'status')
    search_fields = ('document_number', 'vehicle__registration_number')
