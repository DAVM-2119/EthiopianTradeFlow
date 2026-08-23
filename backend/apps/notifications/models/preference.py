from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from .notification import NotificationTypeChoices, NotificationChannelChoices

class NotificationPreference(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        db_index=True
    )
    notification_type = models.CharField(
        max_length=40,
        choices=NotificationTypeChoices.choices
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannelChoices.choices
    )
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
        constraints = [
            models.UniqueConstraint(fields=['user', 'notification_type', 'channel'], name='unique_user_notification_type_channel')
        ]

    def __str__(self):
        state = "ENABLED" if self.enabled else "DISABLED"
        return f"Preference: {self.user.email} [{self.notification_type} + {self.channel}] = {state}"
