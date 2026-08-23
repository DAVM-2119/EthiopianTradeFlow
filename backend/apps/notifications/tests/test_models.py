import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import (
    Notification, NotificationPreference, NotificationTypeChoices,
    NotificationChannelChoices, NotificationStatusChoices
)

@pytest.mark.django_db
def test_notification_and_preference_models():
    user = User.objects.create_user(email='notif_mod@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    notif = Notification.objects.create(
        recipient=user,
        notification_type=NotificationTypeChoices.SHIPMENT_DEPARTED,
        title="Shipment Departed",
        message="Shipment TF-1001 has departed Modjo.",
        channel=NotificationChannelChoices.IN_APP,
        idempotency_key="key-mod-001"
    )

    assert notif.recipient == user
    assert notif.status == NotificationStatusChoices.PENDING
    assert notif.read is False

    pref = NotificationPreference.objects.create(
        user=user,
        notification_type=NotificationTypeChoices.SHIPMENT_DEPARTED,
        channel=NotificationChannelChoices.EMAIL,
        enabled=False
    )

    assert pref.enabled is False
    assert "DISABLED" in str(pref)
