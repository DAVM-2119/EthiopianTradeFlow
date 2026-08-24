import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.services import record_tracking_event
from config.asgi import application

@database_sync_to_async
def create_fanout_test_data():
    shipper = User.objects.create_user(email="shipper_fanout@tradeflow.eth", password="Password123!", role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email="transporter_fanout@tradeflow.eth", password="Password123!", role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email="driver_fanout@tradeflow.eth", password="Password123!", role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="WebSocket Fanout Freight",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        weight=Decimal("25.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("70000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    shipper_token = str(RefreshToken.for_user(shipper).access_token)
    transporter_token = str(RefreshToken.for_user(transporter).access_token)

    return shipment, driver, shipper_token, transporter_token, now

@database_sync_to_async
def record_position_broadcast(shipment_id, driver_user, lat, lon, recorded_at, event_id):
    return record_tracking_event(
        shipment_id=shipment_id,
        driver_user=driver_user,
        latitude=lat,
        longitude=lon,
        speed=Decimal("65.00"),
        heading=Decimal("240.00"),
        recorded_at=recorded_at,
        event_id=event_id
    )

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_websocket_multi_subscriber_fanout():
    shipment, driver, shipper_token, transporter_token, now = await create_fanout_test_data()

    shipper_path = f"/ws/v1/shipments/{shipment.id}/tracking/?token={shipper_token}"
    transporter_path = f"/ws/v1/shipments/{shipment.id}/tracking/?token={transporter_token}"

    comm_shipper = WebsocketCommunicator(application, shipper_path)
    comm_transporter = WebsocketCommunicator(application, transporter_path)

    conn1, _ = await comm_shipper.connect()
    conn2, _ = await comm_transporter.connect()
    assert conn1 and conn2

    await record_position_broadcast(shipment.id, driver, Decimal("11.588300"), Decimal("43.145000"), now, "ws-fanout-001")

    msg_shipper = await comm_shipper.receive_json_from()
    msg_transporter = await comm_transporter.receive_json_from()

    assert msg_shipper["type"] == "tracking.position_updated"
    assert msg_shipper["event_id"] == "ws-fanout-001"
    assert msg_transporter["type"] == "tracking.position_updated"
    assert msg_transporter["event_id"] == "ws-fanout-001"

    await comm_shipper.disconnect()
    await comm_transporter.disconnect()
