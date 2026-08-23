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
def test_full_gps_tracking_api_workflow():
    shipper = User.objects.create_user(email='shipper_tapi@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_tapi@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_tapi@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Freight Load for Tracking API",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("80000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    driver_client = APIClient()
    driver_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(driver).access_token}')

    ingest_url = reverse('tracking-event-ingest')

    resp1 = driver_client.post(ingest_url, {
        "shipment": str(shipment.id),
        "latitude": 9.0054,
        "longitude": 38.7578,
        "speed": 62.5,
        "heading": 91.0,
        "recorded_at": now.isoformat(),
        "event_id": "gps-api-evt-1"
    }, format='json')
    assert resp1.status_code == 201
    assert resp1.json()['data']['event_id'] == "gps-api-evt-1"

    later_time = now + timedelta(minutes=5)
    resp2 = driver_client.post(ingest_url, {
        "shipment": str(shipment.id),
        "latitude": 9.0150,
        "longitude": 38.7650,
        "speed": 68.0,
        "heading": 95.0,
        "recorded_at": later_time.isoformat(),
        "event_id": "gps-api-evt-2"
    }, format='json')
    assert resp2.status_code == 201

    shipper_client = APIClient()
    shipper_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')

    history_url = reverse('shipment-tracking-history', kwargs={'shipment_id': shipment.id})
    history_resp = shipper_client.get(history_url)
    assert history_resp.status_code == 200
    events = history_resp.json()['results']
    assert len(events) == 2
    assert events[0]['event_id'] == "gps-api-evt-2"

    latest_url = reverse('shipment-tracking-latest', kwargs={'shipment_id': shipment.id})
    latest_resp = shipper_client.get(latest_url)
    assert latest_resp.status_code == 200
    assert latest_resp.json()['data']['event_id'] == "gps-api-evt-2"
