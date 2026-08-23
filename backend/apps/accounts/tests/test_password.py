import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

@pytest.mark.django_db
def test_password_change_success():
    user = User.objects.create_user(email='pwd@tradeflow.et', password='OldPassword123!')
    access_token = str(RefreshToken.for_user(user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('auth-password-change')

    payload = {
        "old_password": "OldPassword123!",
        "new_password": "NewPassword123!",
        "new_password_confirm": "NewPassword123!"
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.check_password('NewPassword123!') is True
    assert user.check_password('OldPassword123!') is False


@pytest.mark.django_db
def test_password_reset_flow():
    user = User.objects.create_user(email='reset@tradeflow.et', password='OldPassword123!')
    client = APIClient()

    req_url = reverse('auth-password-reset-request')
    req_resp = client.post(req_url, {"email": "reset@tradeflow.et"}, format='json')
    assert req_resp.status_code == 200
    res_data = req_resp.json()['data']
    assert 'token' in res_data
    assert 'uid' in res_data

    conf_url = reverse('auth-password-reset-confirm')
    conf_payload = {
        "token": f"{res_data['uid']}:{res_data['token']}",
        "new_password": "ResetPassword123!",
        "new_password_confirm": "ResetPassword123!"
    }
    conf_resp = client.post(conf_url, conf_payload, format='json')
    assert conf_resp.status_code == 200

    user.refresh_from_db()
    assert user.check_password('ResetPassword123!') is True
