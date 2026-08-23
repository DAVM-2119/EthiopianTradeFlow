from django.contrib import admin
from .models import TripFuelRecord

@admin.register(TripFuelRecord)
class TripFuelRecordAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'vehicle', 'driver', 'distance_km', 'estimated_fuel_liters', 'actual_fuel_liters', 'fuel_efficiency_km_per_liter', 'data_source', 'recorded_at')
    list_filter = ('data_source', 'recorded_at')
    search_fields = ('shipment__id', 'vehicle__registration_number', 'driver__email')
