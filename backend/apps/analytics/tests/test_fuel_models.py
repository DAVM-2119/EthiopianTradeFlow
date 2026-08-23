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

@pytest.mark.django_db
def test_create_trip_fuel_record_model():
    shipper = User.objects.create_user(email='shipper_fuel_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_fuel_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Fuel M'})
    driver = User.objects.create_user(email='driver_fuel_m@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile,
        registration_number="ETH-FL-001",
        vehicle_type="HEAVY_TRUCK",
        capacity=Decimal("30.00")
    )

    load = Load.objects.create(
        shipper=shipper, title="Fuel Model Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("80000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    record = TripFuelRecord.objects.create(
        shipment=shipment,
        vehicle=vehicle,
        driver=driver,
        distance_km=Decimal("560.00"),
        estimated_fuel_liters=Decimal("196.00"),
        actual_fuel_liters=Decimal("210.00"),
        fuel_efficiency_km_per_liter=Decimal("2.67"),
        fuel_variance_liters=Decimal("14.00"),
        fuel_variance_percentage=Decimal("7.14"),
        data_source=FuelDataSourceChoices.TELEMATICS
    )

    assert record.shipment == shipment
    assert record.vehicle == vehicle
    assert record.driver == driver
    assert record.distance_km == Decimal("560.00")
    assert record.actual_fuel_liters == Decimal("210.00")
    assert "Fuel Record for Shipment" in str(record)
