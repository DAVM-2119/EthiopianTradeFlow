import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.routing.services import calculate_and_save_routes

@pytest.mark.django_db
def test_fuel_analytics_api_endpoints():
    shipper = User.objects.create_user(email='shipper_fuel_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_fuel_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Fuel API'})
    driver = User.objects.create_user(email='driver_fuel_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    unrelated_user = User.objects.create_user(email='unrelated_fuel_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile,
        registration_number="ETH-FL-004",
        vehicle_type="HEAVY_TRUCK",
        capacity=Decimal("30.00")
    )

    load = Load.objects.create(
        shipper=shipper, title="Fuel API Load", origin_city="Addis Ababa", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("75000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    calculate_and_save_routes(shipment_id=shipment.id)

    client = APIClient()
    token_transporter = str(RefreshToken.for_user(transporter_user).access_token)
    token_unrelated = str(RefreshToken.for_user(unrelated_user).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_unrelated}')
    res_unauth = client.post(f'/api/v1/shipments/{shipment.id}/fuel/', {'actual_fuel_liters': '22.00'}, format='json')
    assert res_unauth.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_transporter}')
    res_record = client.post(f'/api/v1/shipments/{shipment.id}/fuel/', {'actual_fuel_liters': '22.00', 'data_source': 'TELEMATICS'}, format='json')
    assert res_record.status_code == status.HTTP_200_OK
    assert res_record.data['data']['actual_fuel_liters'] == '22.00'

    res_get = client.get(f'/api/v1/shipments/{shipment.id}/fuel/')
    assert res_get.status_code == status.HTTP_200_OK
    assert res_get.data['data']['shipment_id'] == str(shipment.id)

    res_v_metrics = client.get(f'/api/v1/vehicles/{vehicle.id}/fuel-metrics/')
    assert res_v_metrics.status_code == status.HTTP_200_OK
    assert res_v_metrics.data['data']['total_trips'] == 1

    res_d_metrics = client.get(f'/api/v1/drivers/{driver.id}/fuel-metrics/')
    assert res_d_metrics.status_code == status.HTTP_200_OK
    assert res_d_metrics.data['data']['total_trips'] == 1

    res_trends = client.get(f'/api/v1/analytics/fuel/trends/?vehicle_id={vehicle.id}')
    assert res_trends.status_code == status.HTTP_200_OK
    assert len(res_trends.data['data']) >= 1

    res_recs = client.get(f'/api/v1/analytics/fuel/recommendations/?vehicle_id={vehicle.id}&driver_id={driver.id}')
    assert res_recs.status_code == status.HTTP_200_OK
