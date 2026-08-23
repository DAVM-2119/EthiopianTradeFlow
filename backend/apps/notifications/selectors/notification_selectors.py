from typing import Optional, List
from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationPreference

def get_user_notifications(user: User, unread_only: bool = False) -> List[Notification]:
    """
    Retrieves notifications for the authenticated user, enforcing user isolation.
    """
    qs = Notification.objects.filter(recipient=user)
    if unread_only:
        qs = qs.filter(read=False)
    return list(qs)


def get_notification_by_id(notification_id, user: Optional[User] = None) -> Optional[Notification]:
    """
    Retrieves notification by ID, optionally verifying recipient ownership.
    """
    qs = Notification.objects.filter(id=notification_id)
    if user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        qs = qs.filter(recipient=user)
    return qs.first()


def get_user_notification_preferences(user: User) -> List[NotificationPreference]:
    """
    Retrieves all notification channel preferences for user.
    """
    return list(NotificationPreference.objects.filter(user=user))
