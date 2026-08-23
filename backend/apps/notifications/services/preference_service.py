from typing import List
from django.db import transaction
from apps.accounts.models import User
from apps.notifications.models import NotificationPreference, NotificationTypeChoices, NotificationChannelChoices

def is_channel_enabled_for_user(*, user_id: str, notification_type: str, channel: str) -> bool:
    """
    Checks if recipient user has enabled notification delivery for a specific type + channel combination.
    Defaults to True if no explicit preference record exists.
    """
    pref = NotificationPreference.objects.filter(
        user_id=user_id,
        notification_type=notification_type,
        channel=channel
    ).first()

    if pref is not None:
        return pref.enabled
    return True


def update_user_preference(*, user_id: str, notification_type: str, channel: str, enabled: bool) -> NotificationPreference:
    """
    Updates or creates notification preference for a user.
    """
    user = User.objects.filter(id=user_id).first()
    with transaction.atomic():
        pref, _ = NotificationPreference.objects.update_or_create(
            user=user,
            notification_type=notification_type,
            channel=channel,
            defaults={'enabled': enabled}
        )
    return pref
