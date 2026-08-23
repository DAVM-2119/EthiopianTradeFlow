import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices

@pytest.mark.django_db
def test_pricing_api_endpoints():
    shipper = User.objects.create_user(email='shipper_p_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    unrelated_user = User.objects.create_user(email='unrelated_p_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Pricing API Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    client = APIClient()
    token_shipper = str(RefreshToken.for_user(shipper).access_token)
    token_unrelated = str(RefreshToken.for_user(unrelated_user).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_unrelated}')
    res_unauth = client.get(f'/api/v1/loads/{load.id}/pricing/')
    assert res_unauth.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    res_detail = client.get(f'/api/v1/loads/{load.id}/pricing/')
    assert res_detail.status_code == status.HTTP_200_OK
    assert res_detail.data['data']['load_id'] == str(load.id)

    res_calc = client.post(f'/api/v1/loads/{load.id}/pricing/calculate/')
    assert res_calc.status_code == status.HTTP_201_CREATED

    res_hist = client.get(f'/api/v1/loads/{load.id}/pricing/history/')
    assert res_hist.status_code == status.HTTP_200_OK
    assert len(res_hist.data['data']) >= 2

    contract_data = {
        "origin_city": "Addis Ababa",
        "destination_city": "Modjo",
        "agreed_rate": "8500.00",
        "valid_from": (now - timedelta(days=1)).isoformat(),
        "valid_until": (now + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    res_contract_create = client.post('/api/v1/pricing/contracts/', contract_data, format='json')
    assert res_contract_create.status_code == status.HTTP_201_CREATED

    res_contract_list = client.get('/api/v1/pricing/contracts/')
    assert res_contract_list.status_code == status.HTTP_200_OK
    assert len(res_contract_list.data['results']) >= 1
