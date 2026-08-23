import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.analytics.models import TripFuelRecord, TransporterPerformance
from apps.analytics.services import generate_monthly_performance, refresh_transporter_performance

@pytest.mark.django_db
def test_generate_monthly_performance_service_and_zero_data_handling():
    shipper = User.objects.create_user(email='shipper_perf_s@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_perf_s@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter, defaults={'business_name': 'Transporter Perf S'})
    driver = User.objects.create_user(email='driver_perf_s@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    perf_zero = generate_monthly_performance(transporter_id=transporter.id, year=now.year, month=now.month)
    assert perf_zero.completed_trips == 0
    assert perf_zero.on_time_delivery_rate == Decimal("0.00")
    assert perf_zero.fuel_efficiency is None
    assert perf_zero.average_rating is None

    vehicle = Vehicle.objects.create(
        transporter=t_profile, registration_number="ETH-PF-001", vehicle_type="HEAVY_TRUCK", capacity=Decimal("30.00")
    )
    load = Load.objects.create(
        shipper=shipper, title="Perf Load", origin_city="Addis", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now - timedelta(days=5), pickup_window_end=now - timedelta(days=4)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("50000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter, vehicle=vehicle, driver=driver,
        status=ShipmentStatusChoices.COMPLETED, delivered_at=now - timedelta(days=2), completed_at=now - timedelta(days=2)
    )

    TripFuelRecord.objects.create(
        shipment=shipment, vehicle=vehicle, driver=driver,
        distance_km=Decimal("400.00"), estimated_fuel_liters=Decimal("100.00"), actual_fuel_liters=Decimal("80.00")
    )

    perf_updated = refresh_transporter_performance(transporter_id=transporter.id, year=now.year, month=now.month)
    assert perf_updated.completed_trips == 1
    assert perf_updated.on_time_delivery_rate == Decimal("100.00")
    assert perf_updated.total_distance_km == Decimal("400.00")
    assert perf_updated.fuel_efficiency == Decimal("5.00")
