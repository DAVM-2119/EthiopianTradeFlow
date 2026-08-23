from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'notification_type', 'channel', 'status', 'read', 'created_at')
    list_filter = ('channel', 'status', 'read', 'notification_type')
    search_fields = ('title', 'message', 'recipient__email', 'idempotency_key')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'channel', 'enabled')
    list_filter = ('channel', 'enabled', 'notification_type')
    search_fields = ('user__email',)
