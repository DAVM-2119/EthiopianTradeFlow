import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.models import User, RoleChoices, StatusChoices

@pytest.mark.django_db
def test_user_registration_success():
    client = APIClient()
    url = reverse('auth-register')
    payload = {
        "email": "newuser@tradeflow.et",
        "first_name": "Haile",
        "last_name": "Gebrselassie",
        "phone_number": "+251911998877",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    data = response.json()
    assert data['success'] is True
    assert data['data']['email'] == 'newuser@tradeflow.et'
    assert data['data']['role'] == RoleChoices.SHIPPER
    assert data['data']['status'] == StatusChoices.PENDING
    assert data['data']['is_verified'] is False

    user = User.objects.get(email='newuser@tradeflow.et')
    assert user.check_password('StrongPassword123!') is True


@pytest.mark.django_db
def test_registration_duplicate_email_rejection():
    User.objects.create_user(email='existing@tradeflow.et', password='Password123!')
    client = APIClient()
    url = reverse('auth-register')
    payload = {
        "email": "existing@tradeflow.et",
        "first_name": "Abebe",
        "last_name": "Bikila",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 400
    assert response.json()['success'] is False


@pytest.mark.django_db
def test_registration_password_mismatch():
    client = APIClient()
    url = reverse('auth-register')
    payload = {
        "email": "mismatch@tradeflow.et",
        "first_name": "Abebe",
        "last_name": "Bikila",
        "password": "Password123!",
        "password_confirm": "DifferentPassword123!"
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_registration_prevents_privilege_injection():
    client = APIClient()
    url = reverse('auth-register')
    payload = {
        "email": "attacker@tradeflow.et",
        "first_name": "Attacker",
        "last_name": "User",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!",
        "role": "ADMIN",
        "is_staff": True,
        "is_superuser": True
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    user = User.objects.get(email='attacker@tradeflow.et')
    assert user.role == RoleChoices.SHIPPER
    assert user.is_staff is False
    assert user.is_superuser is False
