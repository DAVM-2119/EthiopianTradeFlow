import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User

@pytest.mark.django_db
def test_token_refresh_success():
    user = User.objects.create_user(email='refresh@tradeflow.et', password='Password123!')
    refresh_token = str(RefreshToken.for_user(user))

    client = APIClient()
    url = reverse('auth-token-refresh')
    response = client.post(url, {"refresh": refresh_token}, format='json')
    assert response.status_code == 200
    assert 'access' in response.json()
