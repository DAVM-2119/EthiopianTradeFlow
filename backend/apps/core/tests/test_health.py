import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_health_check_endpoint():
    client = APIClient()
    url = reverse('health-check')
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['services']['django'] == 'healthy'
    assert data['services']['database'] == 'healthy'
    assert 'healthy' in data['services']['postgis']
    assert data['services']['redis'] == 'healthy'
