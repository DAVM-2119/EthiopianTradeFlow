from django.contrib import admin
from .models import PriceQuote, ContractRate, PricingAudit

@admin.register(PriceQuote)
class PriceQuoteAdmin(admin.ModelAdmin):
    list_display = ('load', 'final_price', 'currency', 'demand_multiplier', 'fuel_multiplier', 'congestion_multiplier', 'divergence_warning', 'created_at')
    list_filter = ('pricing_method', 'divergence_warning')
    search_fields = ('load__id', 'load__title')

@admin.register(ContractRate)
class ContractRateAdmin(admin.ModelAdmin):
    list_display = ('shipper', 'origin_city', 'destination_city', 'agreed_rate', 'currency', 'is_active', 'valid_until')
    list_filter = ('is_active',)

@admin.register(PricingAudit)
class PricingAuditAdmin(admin.ModelAdmin):
    list_display = ('price_quote', 'algorithm_version', 'calculated_at')
