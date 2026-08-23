from django.contrib import admin
from apps.profiles.models import (
    ShipperProfile,
    TransporterProfile,
    DriverProfile,
    FreightForwarderProfile,
    CustomsStaffProfile,
)

@admin.register(ShipperProfile)
class ShipperProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'trade_license_number', 'city', 'created_at')
    search_fields = ('user__email', 'business_name', 'trade_license_number')


@admin.register(TransporterProfile)
class TransporterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'trade_license_number', 'city', 'created_at')
    search_fields = ('user__email', 'business_name', 'trade_license_number')


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'transporter', 'license_number', 'license_type', 'status', 'created_at')
    list_filter = ('status', 'license_type')
    search_fields = ('user__email', 'license_number')


@admin.register(FreightForwarderProfile)
class FreightForwarderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'trade_license_number', 'city', 'created_at')
    search_fields = ('user__email', 'business_name')


@admin.register(CustomsStaffProfile)
class CustomsStaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'staff_identifier', 'office_location', 'created_at')
    search_fields = ('user__email', 'staff_identifier')
