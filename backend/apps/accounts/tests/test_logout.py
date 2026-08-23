import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

@pytest.mark.django_db
def test_logout_blacklists_refresh_token():
    user = User.objects.create_user(email='logout@tradeflow.et', password='Password123!')
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    url = reverse('auth-logout')

    response = client.post(url, {"refresh": refresh_token}, format='json')
    assert response.status_code == 200

    # Attempting to use blacklisted refresh token to refresh fails
    refresh_url = reverse('auth-token-refresh')
    ref_response = client.post(refresh_url, {"refresh": refresh_token}, format='json')
    assert ref_response.status_code == 401
