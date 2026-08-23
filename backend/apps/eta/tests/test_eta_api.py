import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.eta.services import calculate_and_save_eta

@pytest.mark.django_db
def test_eta_api_endpoints():
    shipper = User.objects.create_user(email='shipper_eta_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_eta_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_eta_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    unrelated_user = User.objects.create_user(email='unrelated_eta_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="ETA API Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("70000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    calculate_and_save_eta(shipment_id=shipment.id)

    client = APIClient()
    token_shipper = str(RefreshToken.for_user(shipper).access_token)
    token_unrelated = str(RefreshToken.for_user(unrelated_user).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_unrelated}')
    res_unauth = client.get(f'/api/v1/shipments/{shipment.id}/eta/')
    assert res_unauth.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    res_eta = client.get(f'/api/v1/shipments/{shipment.id}/eta/')
    assert res_eta.status_code == status.HTTP_200_OK
    assert res_eta.data['data']['shipment_id'] == str(shipment.id)
    assert res_eta.data['data']['prediction_method'] == 'RULE_BASED'

    res_hist = client.get(f'/api/v1/shipments/{shipment.id}/eta/history/')
    assert res_hist.status_code == status.HTTP_200_OK
    assert len(res_hist.data['data']) >= 1
