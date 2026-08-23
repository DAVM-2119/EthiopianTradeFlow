import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import Notification, NotificationTypeChoices, NotificationStatusChoices
from apps.notifications.tasks import send_notification_task

@pytest.mark.django_db
def test_send_notification_task():
    user = User.objects.create_user(email='task_t@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    notif = Notification.objects.create(
        recipient=user,
        notification_type=NotificationTypeChoices.SHIPMENT_CUSTOMS_CLEARED,
        title="Customs Cleared",
        message="Your cargo passed Ethiopian Customs inspection."
    )

    res = send_notification_task(str(notif.id))
    assert res is True

    notif.refresh_from_db()
    assert notif.status == NotificationStatusChoices.SENT
    assert notif.sent_at is not None
