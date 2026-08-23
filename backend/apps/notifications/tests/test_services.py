import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import (
    Notification, NotificationTypeChoices, NotificationChannelChoices, NotificationStatusChoices
)
from apps.notifications.services import (
    create_notification, mark_notification_as_read, mark_all_notifications_as_read,
    update_user_preference
)

@pytest.mark.django_db
def test_notification_services():
    user = User.objects.create_user(email='notif_svc@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    notif = create_notification(
        recipient_id=str(user.id),
        notification_type=NotificationTypeChoices.PAYMENT_COMPLETED,
        title="Payment Successful",
        message="Your payment of 5000 ETB was confirmed.",
        channel=NotificationChannelChoices.IN_APP,
        idempotency_key="idemp-svc-001"
    )

    assert notif is not None
    notif.refresh_from_db()
    assert notif.status == NotificationStatusChoices.SENT

    dup_notif = create_notification(
        recipient_id=str(user.id),
        notification_type=NotificationTypeChoices.PAYMENT_COMPLETED,
        title="Payment Successful",
        message="Your payment of 5000 ETB was confirmed.",
        channel=NotificationChannelChoices.IN_APP,
        idempotency_key="idemp-svc-001"
    )
    assert dup_notif.id == notif.id

    update_user_preference(
        user_id=str(user.id),
        notification_type=NotificationTypeChoices.PAYMENT_COMPLETED,
        channel=NotificationChannelChoices.EMAIL,
        enabled=False
    )

    disabled_notif = create_notification(
        recipient_id=str(user.id),
        notification_type=NotificationTypeChoices.PAYMENT_COMPLETED,
        title="Email Payment Notification",
        message="This should not be created",
        channel=NotificationChannelChoices.EMAIL,
        idempotency_key="idemp-svc-002"
    )
    assert disabled_notif is None

    read_notif = mark_notification_as_read(notification_id=str(notif.id), user_id=str(user.id))
    assert read_notif.read is True
    assert read_notif.read_at is not None

    notif2 = create_notification(
        recipient_id=str(user.id),
        notification_type=NotificationTypeChoices.SECURITY_ALERT,
        title="Security Warning",
        message="Approach zone",
        channel=NotificationChannelChoices.IN_APP,
        idempotency_key="idemp-svc-003"
    )
    count = mark_all_notifications_as_read(user_id=str(user.id))
    assert count >= 1
