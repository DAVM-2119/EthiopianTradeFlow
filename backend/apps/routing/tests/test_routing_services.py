import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.routing.models import Route, RouteStatusChoices
from apps.routing.services import calculate_and_save_routes, propose_reroute, confirm_reroute

@pytest.mark.django_db
def test_routing_service_workflow():
    shipper = User.objects.create_user(email='shipper_rt_srv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_rt_srv@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_rt_srv@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Routing Service Load",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("60000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    active_route = calculate_and_save_routes(shipment_id=shipment.id)
    assert active_route is not None
    assert active_route.status == RouteStatusChoices.ROUTE_ACTIVE
    assert active_route.is_recommended is True

    proposal = propose_reroute(route_id=active_route.id, new_risk_score=0.45)
    assert proposal.status == RouteStatusChoices.REROUTE_PROPOSED
    assert Route.objects.get(id=active_route.id).status == RouteStatusChoices.ROUTE_ACTIVE

    confirmed = confirm_reroute(route_id=proposal.id, accept=True)
    assert confirmed.status == RouteStatusChoices.ROUTE_ACTIVE
    assert Route.objects.get(id=active_route.id).status == RouteStatusChoices.INACTIVE
