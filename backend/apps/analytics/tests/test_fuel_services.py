import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.routing.services import calculate_and_save_routes
from apps.analytics.services import record_trip_fuel, calculate_fuel_efficiency_and_variance, generate_fuel_recommendations

def test_fuel_efficiency_zero_safe_calculations():
    res = calculate_fuel_efficiency_and_variance(
        distance_km=Decimal("500.00"),
        estimated_fuel_liters=Decimal("175.00"),
        actual_fuel_liters=Decimal("200.00")
    )
    assert res['fuel_efficiency'] == Decimal("2.50")
    assert res['fuel_variance_liters'] == Decimal("25.00")
    assert res['fuel_variance_percentage'] == Decimal("14.29")

@pytest.mark.django_db
def test_record_trip_fuel_service():
    shipper = User.objects.create_user(email='shipper_fuel_s@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_fuel_s@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Fuel S'})
    driver = User.objects.create_user(email='driver_fuel_s@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile,
        registration_number="ETH-FL-002",
        vehicle_type="HEAVY_TRUCK",
        capacity=Decimal("30.00")
    )

    load = Load.objects.create(
        shipper=shipper, title="Fuel Service Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("85000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    route = calculate_and_save_routes(shipment_id=shipment.id)

    record = record_trip_fuel(
        shipment_id=shipment.id,
        actual_fuel_liters=Decimal("210.00")
    )

    assert record.shipment == shipment
    assert record.distance_km == route.distance_km
    assert record.actual_fuel_liters == Decimal("210.00")
    assert record.fuel_efficiency_km_per_liter > Decimal("0.00")

    recs = generate_fuel_recommendations(vehicle_id=vehicle.id, driver_id=driver.id)
    assert len(recs) >= 1
