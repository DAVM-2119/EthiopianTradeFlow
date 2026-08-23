from django.contrib import admin
from apps.marketplace.models import Load

@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'shipper', 'origin_city', 'destination_city', 'cargo_type', 'weight', 'status', 'created_at')
    list_filter = ('status', 'cargo_type', 'origin_city', 'destination_city')
    search_fields = ('title', 'shipper__email', 'origin_city', 'destination_city')
    readonly_fields = ('created_at', 'updated_at')
