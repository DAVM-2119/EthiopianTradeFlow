from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom Django UserAdmin handling email-based User model.
    """
    ordering = ['-created_at']
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'is_verified', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'status', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('TradeFlow Identity & Verification', {'fields': ('role', 'status', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'role', 'status'),
        }),
    )

    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login')
