import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import Notification, NotificationTypeChoices
from apps.notifications.permissions import IsNotificationRecipient

@pytest.mark.django_db
def test_notification_permissions():
    u1 = User.objects.create_user(email='perm1@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    u2 = User.objects.create_user(email='perm2@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    n1 = Notification.objects.create(recipient=u1, notification_type=NotificationTypeChoices.SHIPMENT_ARRIVED, title="Arrived", message="Msg")

    perm = IsNotificationRecipient()

    class DummyRequest:
        def __init__(self, user):
            self.user = user

    assert perm.has_object_permission(DummyRequest(u1), None, n1) is True
    assert perm.has_object_permission(DummyRequest(u2), None, n1) is False
