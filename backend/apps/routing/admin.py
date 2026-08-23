from django.contrib import admin
from .models import Route, RouteLeg

class RouteLegInline(admin.TabularInline):
    model = RouteLeg
    extra = 0

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'origin_city', 'destination_city', 'distance_km', 'duration_minutes', 'risk_score', 'optimization_score', 'status', 'is_recommended')
    list_filter = ('status', 'is_recommended', 'provider')
    search_fields = ('shipment__id', 'origin_city', 'destination_city')
    inlines = [RouteLegInline]

@admin.register(RouteLeg)
class RouteLegAdmin(admin.ModelAdmin):
    list_display = ('route', 'sequence', 'start_point', 'end_point', 'distance_km', 'duration_minutes', 'security_risk_score')
