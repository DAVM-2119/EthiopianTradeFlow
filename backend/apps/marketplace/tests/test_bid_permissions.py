import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices

@pytest.mark.django_db
def test_bid_permissions_and_ownership_protection():
    shipper = User.objects.create_user(email='shipper_bp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t1 = User.objects.create_user(email='t1_bp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t2 = User.objects.create_user(email='t2_bp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Load for Permission Test",
        origin_city="Addis Ababa",
        destination_city="Hawassa",
        weight=Decimal("12.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    b1 = Bid.objects.create(load=load, transporter=t1, amount=Decimal("10000.00"), status=BidStatusChoices.ACTIVE)

    client_t2 = APIClient()
    client_t2.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(t2).access_token}')

    detail_url = reverse('bid-detail', kwargs={'pk': b1.id})
    patch_resp = client_t2.patch(detail_url, {"amount": "9000.00"}, format='json')
    assert patch_resp.status_code in (403, 404)

    withdraw_url = reverse('bid-withdraw', kwargs={'pk': b1.id})
    withdraw_resp = client_t2.post(withdraw_url, format='json')
    assert withdraw_resp.status_code == 403

    client_t1 = APIClient()
    client_t1.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(t1).access_token}')
    accept_url = reverse('bid-accept', kwargs={'pk': b1.id})
    accept_resp = client_t1.post(accept_url, format='json')
    assert accept_resp.status_code == 403
