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
from apps.risk.models import RiskZone, IncidentReport, SecurityAlert

@pytest.mark.django_db
def test_risk_api_full_workflow():
    admin = User.objects.create_user(email='admin_risk_api@tradeflow.et', password='Password123!', role=RoleChoices.ADMIN, is_staff=True)
    shipper = User.objects.create_user(email='shipper_risk_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_risk_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Risk API'})
    driver = User.objects.create_user(email='driver_risk_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile, registration_number="ETH-RZ-003", vehicle_type="HEAVY_TRUCK", capacity=Decimal("30.00")
    )
    load = Load.objects.create(
        shipper=shipper, title="Risk API Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("85000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    client = APIClient()
    token_admin = str(RefreshToken.for_user(admin).access_token)
    token_driver = str(RefreshToken.for_user(driver).access_token)
    token_shipper = str(RefreshToken.for_user(shipper).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin}')
    payload_zone = {
        "name": "Djibouti Highway Risk Zone",
        "description": "High threat area",
        "latitude": "11.500000",
        "longitude": "42.100000",
        "radius_km": "12.00",
        "severity": "HIGH",
        "source": "ADMIN"
    }
    res_z = client.post('/api/v1/risk-zones/', payload_zone, format='json')
    assert res_z.status_code == status.HTTP_201_CREATED
    zone_id = res_z.data['data']['id']

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    res_z_unauth = client.post('/api/v1/risk-zones/', payload_zone, format='json')
    assert res_z_unauth.status_code == status.HTTP_403_FORBIDDEN

    res_z_list = client.get('/api/v1/risk-zones/')
    assert res_z_list.status_code == status.HTTP_200_OK
    assert len(res_z_list.data['data']) >= 1

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_driver}')
    payload_inc = {
        "shipment_id": str(shipment.id),
        "incident_type": "CHECKPOINT_DELAY",
        "description": "Customs inspection blockage",
        "latitude": "11.480000",
        "longitude": "42.080000",
        "severity": "MEDIUM"
    }
    res_inc = client.post('/api/v1/incidents/', payload_inc, format='json')
    assert res_inc.status_code == status.HTTP_201_CREATED
    inc_id = res_inc.data['data']['id']

    payload_check = {
        "shipment_id": str(shipment.id),
        "latitude": "11.490000",
        "longitude": "42.090000"
    }
    res_check = client.post('/api/v1/risk/check-location/', payload_check, format='json')
    assert res_check.status_code == status.HTTP_200_OK
    assert res_check.data['data']['risk_detected'] is True
    assert len(res_check.data['data']['generated_alerts']) >= 1
    alert_id = res_check.data['data']['generated_alerts'][0]['id']

    res_alerts = client.get(f'/api/v1/security-alerts/?shipment_id={shipment.id}')
    assert res_alerts.status_code == status.HTTP_200_OK
    assert len(res_alerts.data['data']) >= 1

    res_ack = client.post(f'/api/v1/security-alerts/{alert_id}/acknowledge/')
    assert res_ack.status_code == status.HTTP_200_OK
    assert res_ack.data['data']['status'] == 'ACKNOWLEDGED'
