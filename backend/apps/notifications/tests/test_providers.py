import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import Notification, NotificationTypeChoices, NotificationChannelChoices
from apps.notifications.providers import get_notification_provider, MockEmailProvider, MockSMSProvider, MockPushProvider

@pytest.mark.django_db
def test_notification_providers():
    user = User.objects.create_user(email='prov_t@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    notif_email = Notification.objects.create(recipient=user, notification_type=NotificationTypeChoices.SHIPMENT_DEPARTED, title="Email", message="Body", channel=NotificationChannelChoices.EMAIL)
    email_prov = get_notification_provider("EMAIL")
    assert isinstance(email_prov, MockEmailProvider)
    res_e = email_prov.send(notification=notif_email)
    assert res_e["success"] is True

    notif_sms = Notification.objects.create(recipient=user, notification_type=NotificationTypeChoices.SECURITY_ALERT, title="SMS", message="Body", channel=NotificationChannelChoices.SMS)
    sms_prov = get_notification_provider("SMS")
    assert isinstance(sms_prov, MockSMSProvider)
    res_s = sms_prov.send(notification=notif_sms)
    assert res_s["success"] is True

    notif_push = Notification.objects.create(recipient=user, notification_type=NotificationTypeChoices.PAYMENT_COMPLETED, title="Push", message="Body", channel=NotificationChannelChoices.PUSH)
    push_prov = get_notification_provider("PUSH")
    assert isinstance(push_prov, MockPushProvider)
    res_p = push_prov.send(notification=notif_push)
    assert res_p["success"] is True
