import uuid
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from apps.core.exceptions import NotFoundException, ValidationException, PermissionDeniedException
from apps.accounts.models import User
from apps.notifications.models import (
    Notification, NotificationStatusChoices, NotificationChannelChoices,
    NotificationPriorityChoices
)
from apps.notifications.services.preference_service import is_channel_enabled_for_user
from apps.notifications.tasks.notification_tasks import send_notification_task

def create_notification(
    *,
    recipient_id: str,
    notification_type: str,
    title: str,
    message: str,
    channel: str = NotificationChannelChoices.IN_APP,
    idempotency_key: Optional[str] = None,
    priority: str = NotificationPriorityChoices.NORMAL,
    data: Optional[Dict[str, Any]] = None,
    related_object_type: str = '',
    related_object_id: str = ''
) -> Optional[Notification]:
    """
    FR-03.3 & Cross-System Notification Core Entrypoint.
    Creates notification record if recipient has enabled the channel in their preferences.
    Enforces idempotency keys to prevent duplicate notifications.
    Dispatches Celery async delivery task.
    """
    recipient = User.objects.filter(id=recipient_id).first()
    if not recipient:
        raise NotFoundException("Recipient user not found.")

    if idempotency_key:
        existing = Notification.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    if not is_channel_enabled_for_user(user_id=recipient.id, notification_type=notification_type, channel=channel):
        return None

    key = idempotency_key or f"notif-{uuid.uuid4().hex}"

    with transaction.atomic():
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            status=NotificationStatusChoices.PENDING,
            priority=priority,
            related_object_type=related_object_type,
            related_object_id=str(related_object_id),
            data=data or {},
            idempotency_key=key
        )

    send_notification_task.delay(str(notification.id))

    return notification


def mark_notification_as_read(*, notification_id: str, user_id: str) -> Notification:
    """
    Marks single notification as read by recipient.
    """
    notification = Notification.objects.filter(id=notification_id).first()
    if not notification:
        raise NotFoundException("Notification not found.")

    if str(notification.recipient_id) != str(user_id):
        raise PermissionDeniedException("You are not authorized to mark another user's notification as read.")

    if not notification.read:
        notification.read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['read', 'read_at', 'updated_at'])

    return notification


def mark_all_notifications_as_read(*, user_id: str) -> int:
    """
    Marks all unread notifications for a user as read.
    """
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise NotFoundException("User not found.")

    now = timezone.now()
    count = Notification.objects.filter(recipient=user, read=False).update(read=True, read_at=now, updated_at=now)
    return count
