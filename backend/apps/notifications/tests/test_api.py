import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User, RoleChoices
from apps.notifications.models import Notification, NotificationTypeChoices, NotificationChannelChoices

@pytest.mark.django_db
def test_notification_api_endpoints():
    u1 = User.objects.create_user(email='api_u1@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    u2 = User.objects.create_user(email='api_u2@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    n1 = Notification.objects.create(recipient=u1, notification_type=NotificationTypeChoices.SHIPMENT_DEPARTED, title="Departed", message="Msg 1")
    n2 = Notification.objects.create(recipient=u2, notification_type=NotificationTypeChoices.SECURITY_ALERT, title="Alert", message="Msg 2")

    client = APIClient()
    token_u1 = str(RefreshToken.for_user(u1).access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_u1}')

    res_list = client.get('/api/v1/notifications/')
    assert res_list.status_code == status.HTTP_200_OK
    assert len(res_list.data['data']) == 1
    assert res_list.data['data'][0]['id'] == str(n1.id)

    res_detail = client.get(f'/api/v1/notifications/{n1.id}/')
    assert res_detail.status_code == status.HTTP_200_OK
    assert res_detail.data['data']['title'] == "Departed"

    res_forbidden = client.get(f'/api/v1/notifications/{n2.id}/')
    assert res_forbidden.status_code == status.HTTP_404_NOT_FOUND

    res_read = client.post(f'/api/v1/notifications/{n1.id}/read/')
    assert res_read.status_code == status.HTTP_200_OK
    assert res_read.data['data']['read'] is True

    res_read_all = client.post('/api/v1/notifications/read-all/')
    assert res_read_all.status_code == status.HTTP_200_OK

    res_prefs = client.get('/api/v1/notifications/preferences/')
    assert res_prefs.status_code == status.HTTP_200_OK

    res_upd = client.patch('/api/v1/notifications/preferences/update/', {
        'notification_type': 'SHIPMENT_DEPARTED',
        'channel': 'SMS',
        'enabled': False
    }, format='json')
    assert res_upd.status_code == status.HTTP_200_OK
    assert res_upd.data['data']['enabled'] is False
