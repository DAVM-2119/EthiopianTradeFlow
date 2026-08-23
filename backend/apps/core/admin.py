from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'resource_type', 'resource_id', 'actor_id', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('actor_id', 'resource_type', 'resource_id')
    readonly_fields = ('id', 'actor_id', 'action', 'resource_type', 'resource_id', 'metadata', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
