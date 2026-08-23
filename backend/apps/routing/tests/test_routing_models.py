import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.routing.models import Route, RouteLeg, RouteStatusChoices

@pytest.mark.django_db
def test_create_route_and_route_leg_models():
    shipper = User.objects.create_user(email='shipper_rt_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_rt_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_rt_m@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Routing Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("50000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    route = Route.objects.create(
        shipment=shipment,
        provider='OSRM',
        provider_route_id='osrm-rt-001',
        origin_city="Addis Ababa",
        destination_city="Modjo",
        distance_km=Decimal("65.00"),
        duration_minutes=78,
        estimated_fuel_liters=Decimal("22.75"),
        estimated_fuel_cost=Decimal("2047.50"),
        risk_score=Decimal("0.10"),
        optimization_score=Decimal("0.1250"),
        status=RouteStatusChoices.ROUTE_ACTIVE,
        is_recommended=True,
        geometry_json={"type": "LineString", "coordinates": []}
    )

    leg = RouteLeg.objects.create(
        route=route,
        sequence=1,
        start_point="Addis Ababa",
        end_point="Modjo",
        distance_km=Decimal("65.00"),
        duration_minutes=78,
        estimated_fuel_liters=Decimal("22.75"),
        security_risk_score=Decimal("0.10")
    )

    assert route.shipment == shipment
    assert route.is_recommended is True
    assert "Route for Shipment" in str(route)
    assert leg.route == route
    assert "Leg 1" in str(leg)
