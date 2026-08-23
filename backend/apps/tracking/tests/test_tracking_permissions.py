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
from apps.tracking.services import record_tracking_event

@pytest.mark.django_db
def test_tracking_permissions_read_and_write_access():
    shipper = User.objects.create_user(email='shipper_tp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_tp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_tp@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    unrelated_user = User.objects.create_user(email='unrelated_tp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Permission Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("30000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    record_tracking_event(
        shipment_id=shipment.id,
        driver_user=driver,
        latitude=Decimal("8.980000"),
        longitude=Decimal("38.790000"),
        recorded_at=now
    )

    history_url = reverse('shipment-tracking-history', kwargs={'shipment_id': shipment.id})

    unrelated_client = APIClient()
    unrelated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(unrelated_user).access_token}')
    assert unrelated_client.get(history_url).status_code == 403

    shipper_client = APIClient()
    shipper_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')
    assert shipper_client.get(history_url).status_code == 200

    transporter_client = APIClient()
    transporter_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(transporter).access_token}')
    assert transporter_client.get(history_url).status_code == 200
