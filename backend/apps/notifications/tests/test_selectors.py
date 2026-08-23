import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import Notification, NotificationTypeChoices
from apps.notifications.selectors import (
    get_user_notifications, get_notification_by_id, get_user_notification_preferences
)

@pytest.mark.django_db
def test_notification_selectors():
    u1 = User.objects.create_user(email='user1_sel@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    u2 = User.objects.create_user(email='user2_sel@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    n1 = Notification.objects.create(recipient=u1, notification_type=NotificationTypeChoices.SHIPMENT_DEPARTED, title="Title 1", message="Msg 1")
    n2 = Notification.objects.create(recipient=u2, notification_type=NotificationTypeChoices.SECURITY_ALERT, title="Title 2", message="Msg 2")

    u1_notifs = get_user_notifications(u1)
    assert len(u1_notifs) == 1
    assert u1_notifs[0] == n1

    assert get_notification_by_id(n1.id, user=u1) == n1
    assert get_notification_by_id(n1.id, user=u2) is None
