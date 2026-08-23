import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.models import User, StatusChoices

@pytest.mark.django_db
def test_login_success():
    User.objects.create_user(
        email='loginuser@tradeflow.et',
        password='MyPassword123!',
        status=StatusChoices.ACTIVE
    )
    client = APIClient()
    url = reverse('auth-login')
    payload = {"email": "loginuser@tradeflow.et", "password": "MyPassword123!"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'access' in data['data']
    assert 'refresh' in data['data']
    assert data['data']['user']['email'] == 'loginuser@tradeflow.et'


@pytest.mark.django_db
def test_login_invalid_password_returns_generic_error():
    User.objects.create_user(email='loginuser@tradeflow.et', password='MyPassword123!')
    client = APIClient()
    url = reverse('auth-login')
    payload = {"email": "loginuser@tradeflow.et", "password": "WrongPassword!"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 400
    assert response.json()['error']['message'] == "Invalid email or password."


@pytest.mark.django_db
def test_login_nonexistent_email_returns_generic_error():
    client = APIClient()
    url = reverse('auth-login')
    payload = {"email": "nobody@tradeflow.et", "password": "AnyPassword!"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 400
    assert response.json()['error']['message'] == "Invalid email or password."


@pytest.mark.django_db
def test_login_suspended_or_inactive_user_rejected():
    User.objects.create_user(
        email='suspended@tradeflow.et',
        password='Password123!',
        status=StatusChoices.SUSPENDED
    )
    client = APIClient()
    url = reverse('auth-login')
    payload = {"email": "suspended@tradeflow.et", "password": "Password123!"}
    response = client.post(url, payload, format='json')
    assert response.status_code == 403
    assert "suspended" in response.json()['error']['message'].lower()
