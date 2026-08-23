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
from apps.routing.services import calculate_and_save_routes

@pytest.mark.django_db
def test_routing_api_endpoints():
    shipper = User.objects.create_user(email='shipper_rt_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_rt_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_rt_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    unrelated_user = User.objects.create_user(email='unrelated_rt_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Routing API Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("70000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    client = APIClient()
    token_shipper = str(RefreshToken.for_user(shipper).access_token)
    token_unrelated = str(RefreshToken.for_user(unrelated_user).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_unrelated}')
    res_unauth = client.post(f'/api/v1/shipments/{shipment.id}/routes/calculate/')
    assert res_unauth.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    res_calc = client.post(f'/api/v1/shipments/{shipment.id}/routes/calculate/')
    assert res_calc.status_code == status.HTTP_201_CREATED
    route_id = res_calc.data['data']['id']

    res_list = client.get(f'/api/v1/shipments/{shipment.id}/routes/')
    assert res_list.status_code == status.HTTP_200_OK
    assert len(res_list.data['data']) >= 1

    res_detail = client.get(f'/api/v1/routes/{route_id}/')
    assert res_detail.status_code == status.HTTP_200_OK
    assert res_detail.data['data']['id'] == route_id

    res_prop = client.post(f'/api/v1/routes/{route_id}/reroute/', {'action': 'propose', 'new_risk_score': 0.40}, format='json')
    assert res_prop.status_code == status.HTTP_200_OK
    prop_id = res_prop.data['data']['id']

    res_conf = client.post(f'/api/v1/routes/{prop_id}/reroute/', {'action': 'confirm'}, format='json')
    assert res_conf.status_code == status.HTTP_200_OK
    assert res_conf.data['data']['status'] == 'ROUTE_ACTIVE'
