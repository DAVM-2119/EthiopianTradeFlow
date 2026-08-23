import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices

@pytest.mark.django_db
def test_shipment_permissions_isolation():
    s1 = User.objects.create_user(email='s1_sp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    s2 = User.objects.create_user(email='s2_sp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t1 = User.objects.create_user(email='t1_sp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=s1,
        title="Permission Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(load=load, transporter=t1, amount=Decimal("30000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=s1, transporter=t1, status=ShipmentStatusChoices.BOOKED)

    client_s2 = APIClient()
    client_s2.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(s2).access_token}')

    detail_url = reverse('shipment-detail', kwargs={'pk': shipment.id})
    detail_resp = client_s2.get(detail_url)
    assert detail_resp.status_code == 403
