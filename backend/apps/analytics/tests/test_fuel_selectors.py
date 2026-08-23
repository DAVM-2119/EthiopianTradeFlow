import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.analytics.models import TripFuelRecord, FuelDataSourceChoices
from apps.analytics.selectors import (
    get_vehicle_fuel_summary,
    get_driver_fuel_summary,
    get_fuel_trends_data
)

@pytest.mark.django_db
def test_fuel_selectors_aggregations():
    shipper = User.objects.create_user(email='shipper_fuel_sel@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_fuel_sel@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Fuel Sel'})
    driver = User.objects.create_user(email='driver_fuel_sel@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile,
        registration_number="ETH-FL-003",
        vehicle_type="HEAVY_TRUCK",
        capacity=Decimal("30.00")
    )

    load = Load.objects.create(
        shipper=shipper, title="Fuel Selector Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("85000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    TripFuelRecord.objects.create(
        shipment=shipment,
        vehicle=vehicle,
        driver=driver,
        distance_km=Decimal("500.00"),
        estimated_fuel_liters=Decimal("175.00"),
        actual_fuel_liters=Decimal("200.00"),
        fuel_efficiency_km_per_liter=Decimal("2.50"),
        fuel_variance_liters=Decimal("25.00"),
        fuel_variance_percentage=Decimal("14.29"),
        data_source=FuelDataSourceChoices.MANUAL
    )

    veh_summary = get_vehicle_fuel_summary(vehicle.id)
    assert veh_summary['total_trips'] == 1
    assert veh_summary['total_distance_km'] == 500.00
    assert veh_summary['total_actual_fuel_liters'] == 200.00
    assert veh_summary['average_fuel_efficiency_km_per_liter'] == 2.50

    drv_summary = get_driver_fuel_summary(driver.id)
    assert drv_summary['total_trips'] == 1
    assert drv_summary['total_distance_km'] == 500.00

    trends = get_fuel_trends_data(vehicle_id=vehicle.id, period='monthly')
    assert len(trends) >= 1
    assert trends[0]['trip_count'] == 1
