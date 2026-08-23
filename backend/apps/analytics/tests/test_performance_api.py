import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.analytics.models import TransporterPerformance

@pytest.mark.django_db
def test_transporter_performance_api_workflow():
    transporter1 = User.objects.create_user(email='t1_perf_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    transporter2 = User.objects.create_user(email='t2_perf_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    shipper = User.objects.create_user(email='shipper_perf_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)

    client = APIClient()
    token_t1 = str(RefreshToken.for_user(transporter1).access_token)
    token_t2 = str(RefreshToken.for_user(transporter2).access_token)
    token_shipper = str(RefreshToken.for_user(shipper).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    res_shipper = client.get('/api/v1/analytics/transporter/performance/')
    assert res_shipper.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_t1}')
    res_dash = client.get('/api/v1/analytics/transporter/performance/')
    assert res_dash.status_code == status.HTTP_200_OK
    assert 'performance' in res_dash.data['data']
    assert 'corridor_benchmark' in res_dash.data['data']
    assert res_dash.data['data']['performance']['transporter_id'] == str(transporter1.id)

    res_other = client.get(f'/api/v1/analytics/transporter/performance/?transporter_id={transporter2.id}')
    assert res_other.status_code == status.HTTP_403_FORBIDDEN

    res_hist = client.get('/api/v1/analytics/transporter/performance/history/')
    assert res_hist.status_code == status.HTTP_200_OK
    assert isinstance(res_hist.data['data'], list)
