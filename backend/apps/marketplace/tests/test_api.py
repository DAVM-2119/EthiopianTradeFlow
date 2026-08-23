import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, CargoTypeChoices

@pytest.mark.django_db
def test_shipper_load_creation_and_posting_via_api():
    shipper = User.objects.create_user(email='shipper_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')
    url = reverse('load-list-create')

    payload = {
        "title": "40 Tons Wheat Import",
        "origin_city": "Djibouti Port",
        "destination_city": "Modjo Dry Port",
        "cargo_type": CargoTypeChoices.DRY_BULK,
        "weight": "40.00",
        "pickup_window_start": (now + timedelta(days=1)).isoformat(),
        "pickup_window_end": (now + timedelta(days=2)).isoformat()
    }

    create_resp = client.post(url, payload, format='json')
    assert create_resp.status_code == 201
    load_id = create_resp.json()['id']
    assert create_resp.json()['status'] == LoadStatusChoices.DRAFT

    post_url = reverse('load-post', kwargs={'pk': load_id})
    post_resp = client.post(post_url, format='json')
    assert post_resp.status_code == 200
    assert post_resp.json()['data']['status'] == LoadStatusChoices.POSTED

    cancel_url = reverse('load-cancel', kwargs={'pk': load_id})
    cancel_resp = client.post(cancel_url, format='json')
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()['data']['status'] == LoadStatusChoices.CANCELLED
