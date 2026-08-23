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
def test_load_search_filtering_and_pagination():
    shipper = User.objects.create_user(email='shipper_srch@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_srch@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    Load.objects.create(
        shipper=shipper,
        title="Load 1 - Djibouti to Modjo",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        cargo_type=CargoTypeChoices.CONTAINERIZED,
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    Load.objects.create(
        shipper=shipper,
        title="Load 2 - Djibouti to Hawassa",
        origin_city="Djibouti Port",
        destination_city="Hawassa",
        cargo_type=CargoTypeChoices.REFRIGERATED,
        weight=Decimal("15.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=2),
        pickup_window_end=now + timedelta(days=3)
    )
    Load.objects.create(
        shipper=shipper,
        title="Load 3 - Draft Load",
        origin_city="Addis Ababa",
        destination_city="Mekelle",
        cargo_type=CargoTypeChoices.GENERAL_CARGO,
        weight=Decimal("10.00"),
        status=LoadStatusChoices.DRAFT,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(transporter).access_token}')
    url = reverse('load-list-create')

    resp = client.get(url)
    assert resp.status_code == 200
    results = resp.json()['results']
    assert len(results) == 2

    filtered_resp = client.get(f"{url}?destination_city=Hawassa")
    assert filtered_resp.status_code == 200
    f_results = filtered_resp.json()['results']
    assert len(f_results) == 1
    assert f_results[0]['destination_city'] == "Hawassa"
