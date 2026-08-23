from django.contrib import admin
from apps.marketplace.models import Load, Bid

@admin.register(Load)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'shipper', 'origin_city', 'destination_city', 'cargo_type', 'weight', 'status', 'created_at')
    list_filter = ('status', 'cargo_type', 'origin_city', 'destination_city')
    search_fields = ('title', 'shipper__email', 'origin_city', 'destination_city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'load', 'transporter', 'amount', 'currency', 'status', 'accepted_at', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('load__title', 'transporter__email', 'message')
    readonly_fields = ('load', 'transporter', 'status', 'accepted_at', 'withdrawn_at', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False
