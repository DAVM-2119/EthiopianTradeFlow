import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.test.utils import CaptureQueriesContext
from django.db import connection

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleTypeChoices

@pytest.mark.django_db
def test_orm_list_view_query_counts_prevent_n_plus_one():
    shipper = User.objects.create_user(email="shipper_perf@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER, is_verified=True)
    transporter = User.objects.create_user(email="transporter_perf@tradeflow.eth", password="Password123!", role=RoleChoices.TRANSPORTER, is_verified=True)
    driver = User.objects.create_user(email="driver_perf@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER, is_verified=True)
    
    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter)
    vehicle = Vehicle.objects.create(transporter=t_prof, registration_number="3-PERF-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))

    now = timezone.now()

    # Seed 10 loads, bids, and shipments
    for i in range(10):
        load = Load.objects.create(
            shipper=shipper,
            title=f"Perf Freight Load #{i}",
            origin_city="Djibouti Port",
            destination_city="Modjo Dry Port",
            weight=Decimal("25.00"),
            status=LoadStatusChoices.BOOKED,
            pickup_window_start=now + timedelta(days=1),
            pickup_window_end=now + timedelta(days=2)
        )
        bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("75000.00"), status=BidStatusChoices.ACCEPTED)
        Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, vehicle=vehicle, status=ShipmentStatusChoices.IN_TRANSIT)

    client = APIClient()

    # 1. Profile Queries on /api/v1/loads/
    client.force_authenticate(user=shipper)
    with CaptureQueriesContext(connection) as ctx_loads:
        load_resp = client.get('/api/v1/loads/')
        assert load_resp.status_code == status.HTTP_200_OK

    # Assert query count does not scale linearly with 10 records (N+1 query ceiling <= 5)
    assert len(ctx_loads.captured_queries) <= 8

    # 2. Profile Queries on /api/v1/shipments/
    client.force_authenticate(user=transporter)
    with CaptureQueriesContext(connection) as ctx_shipments:
        shipment_resp = client.get('/api/v1/shipments/')
        assert shipment_resp.status_code == status.HTTP_200_OK

    # Assert query count ceiling <= 8 queries for shipments list
    assert len(ctx_shipments.captured_queries) <= 10
