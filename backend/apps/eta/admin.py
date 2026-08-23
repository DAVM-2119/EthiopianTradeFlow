from django.contrib import admin
from .models import ETAPrediction

@admin.register(ETAPrediction)
class ETAPredictionAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'estimated_arrival', 'remaining_distance_km', 'expected_speed_kmh', 'delay_minutes', 'prediction_method', 'predicted_at')
    list_filter = ('prediction_method', 'algorithm_version')
    search_fields = ('shipment__id', 'shipment__load__title')
    readonly_fields = ('predicted_at',)
