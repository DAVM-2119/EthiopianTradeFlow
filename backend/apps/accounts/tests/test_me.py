import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

@pytest.mark.django_db
def test_me_authenticated_user_success():
    user = User.objects.create_user(
        email='me@tradeflow.et',
        password='Password123!',
        first_name='Kenenisa',
        last_name='Bekele'
    )
    access_token = str(RefreshToken.for_user(user).access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('auth-me')

    response = client.get(url)
    assert response.status_code == 200
    data = response.json()['data']
    assert data['email'] == 'me@tradeflow.et'
    assert data['first_name'] == 'Kenenisa'
    assert 'password' not in data


@pytest.mark.django_db
def test_me_unauthenticated_request_rejected():
    client = APIClient()
    url = reverse('auth-me')
    response = client.get(url)
    assert response.status_code == 401
