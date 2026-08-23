import logging
from celery import shared_task
from apps.notifications.models import Notification, NotificationStatusChoices
from apps.notifications.providers import get_notification_provider

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_notification_task(self, notification_id: str):
    """
    Celery task handling asynchronous notification delivery with retries.
    """
    try:
        notification = Notification.objects.filter(id=notification_id).first()
        if not notification:
            logger.warning(f"Notification #{notification_id} not found for async task execution.")
            return False

        if notification.status == NotificationStatusChoices.SENT:
            return True

        notification.status = NotificationStatusChoices.PROCESSING
        notification.save(update_fields=['status', 'updated_at'])

        provider = get_notification_provider(notification.channel)
        res = provider.send(notification=notification)

        from django.utils import timezone
        notification.status = NotificationStatusChoices.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['status', 'sent_at', 'updated_at'])
        return True

    except Exception as exc:
        logger.error(f"Error executing send_notification_task for #{notification_id}: {exc}")
        notification = Notification.objects.filter(id=notification_id).first()
        if notification:
            notification.retry_count += 1
            notification.failure_reason = str(exc)
            if self.request.retries >= self.max_retries:
                notification.status = NotificationStatusChoices.FAILED
            else:
                notification.status = NotificationStatusChoices.RETRYING
            notification.save(update_fields=['retry_count', 'failure_reason', 'status', 'updated_at'])

        raise self.retry(exc=exc)
