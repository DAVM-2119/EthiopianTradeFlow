from django.contrib import admin
from apps.verification.models import Verification, VerificationHistory

class VerificationHistoryInline(admin.TabularInline):
    model = VerificationHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'reason', 'notes', 'created_at')
    can_delete = False

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'verified_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('submitted_at', 'verified_at', 'suspended_at', 'created_at', 'updated_at')
    inlines = [VerificationHistoryInline]


@admin.register(VerificationHistory)
class VerificationHistoryAdmin(admin.ModelAdmin):
    list_display = ('verification', 'previous_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('previous_status', 'new_status')
    search_fields = ('verification__user__email', 'changed_by__email', 'reason')
    readonly_fields = ('verification', 'previous_status', 'new_status', 'changed_by', 'reason', 'notes', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
