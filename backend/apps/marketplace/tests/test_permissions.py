import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices

@pytest.mark.django_db
def test_load_ownership_security_isolation():
    s1 = User.objects.create_user(email='s1_own@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    s2 = User.objects.create_user(email='s2_own@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=s1,
        title="Shipper 1 Load",
        origin_city="Addis Ababa",
        destination_city="Adama",
        weight=Decimal("15.00"),
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(s2).access_token}')

    detail_url = reverse('load-detail', kwargs={'pk': load.id})
    patch_resp = client.patch(detail_url, {"title": "Hacked Title"}, format='json')
    assert patch_resp.status_code in (403, 404)

    post_url = reverse('load-post', kwargs={'pk': load.id})
    post_resp = client.post(post_url, format='json')
    assert post_resp.status_code in (403, 404)


@pytest.mark.django_db
def test_transporter_cannot_create_load():
    transporter = User.objects.create_user(email='t_no_create@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(transporter).access_token}')
    url = reverse('load-list-create')

    payload = {
        "title": "Transporter illegal load",
        "origin_city": "Modjo",
        "destination_city": "Djibouti",
        "weight": "25.00",
        "pickup_window_start": (now + timedelta(days=1)).isoformat(),
        "pickup_window_end": (now + timedelta(days=2)).isoformat()
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 403
