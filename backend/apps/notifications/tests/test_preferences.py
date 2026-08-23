import pytest
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import NotificationTypeChoices, NotificationChannelChoices
from apps.notifications.services import is_channel_enabled_for_user, update_user_preference

@pytest.mark.django_db
def test_preferences_logic():
    user = User.objects.create_user(email='pref_t@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    assert is_channel_enabled_for_user(user_id=str(user.id), notification_type=NotificationTypeChoices.SECURITY_ALERT, channel=NotificationChannelChoices.SMS) is True

    update_user_preference(user_id=str(user.id), notification_type=NotificationTypeChoices.SECURITY_ALERT, channel=NotificationChannelChoices.SMS, enabled=False)

    assert is_channel_enabled_for_user(user_id=str(user.id), notification_type=NotificationTypeChoices.SECURITY_ALERT, channel=NotificationChannelChoices.SMS) is False

    update_user_preference(user_id=str(user.id), notification_type=NotificationTypeChoices.SECURITY_ALERT, channel=NotificationChannelChoices.SMS, enabled=True)

    assert is_channel_enabled_for_user(user_id=str(user.id), notification_type=NotificationTypeChoices.SECURITY_ALERT, channel=NotificationChannelChoices.SMS) is True
