from django.contrib import admin
from .models import Payment, PaymentTransaction, Commission, Payout, Settlement, PaymentDispute

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'payer', 'amount', 'currency', 'status', 'provider', 'created_at')
    list_filter = ('status', 'provider', 'currency')
    search_fields = ('id', 'idempotency_key', 'provider_transaction_id')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'provider', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'provider')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'rate', 'gross_amount', 'commission_amount', 'net_amount', 'calculated_at')

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'transporter', 'payment', 'gross_amount', 'commission_amount', 'net_amount', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'payment', 'gross_amount', 'commission_amount', 'net_transporter_amount', 'status', 'reconciled_at')
    list_filter = ('status',)

@admin.register(PaymentDispute)
class PaymentDisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'raised_by', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
