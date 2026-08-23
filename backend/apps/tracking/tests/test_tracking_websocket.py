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
def create_test_data():
    shipper = User.objects.create_user(email='shipper_ws@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_ws@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_ws@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    unrelated_user = User.objects.create_user(email='unrelated_ws@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="WebSocket Tracking Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("50000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    shipper_token = str(RefreshToken.for_user(shipper).access_token)
    unrelated_token = str(RefreshToken.for_user(unrelated_user).access_token)

    return shipment, driver, shipper_token, unrelated_token, now


@database_sync_to_async
def record_event_sync(shipment_id, driver_user, lat, lon, recorded_at, event_id):
    return record_tracking_event(
        shipment_id=shipment_id,
        driver_user=driver_user,
        latitude=lat,
        longitude=lon,
        speed=Decimal("60.00"),
        heading=Decimal("90.00"),
        recorded_at=recorded_at,
        event_id=event_id
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_websocket_tracking_workflow():
    shipment, driver, shipper_token, unrelated_token, now = await create_test_data()

    unrelated_path = f"/ws/v1/shipments/{shipment.id}/tracking/?token={unrelated_token}"
    communicator_unrelated = WebsocketCommunicator(application, unrelated_path)
    connected, close_code = await communicator_unrelated.connect()
    assert not connected
    assert close_code == 4003

    shipper_path = f"/ws/v1/shipments/{shipment.id}/tracking/?token={shipper_token}"
    communicator_shipper = WebsocketCommunicator(application, shipper_path)
    connected_shipper, _ = await communicator_shipper.connect()
    assert connected_shipper

    event = await record_event_sync(shipment.id, driver, Decimal("9.005400"), Decimal("38.757800"), now, "ws-evt-001")

    response = await communicator_shipper.receive_json_from()
    assert response["type"] == "tracking.position_updated"
    assert response["shipment_id"] == str(shipment.id)
    assert response["event_id"] == "ws-evt-001"
    assert response["latitude"] == 9.0054
    assert response["longitude"] == 38.7578

    await communicator_shipper.disconnect()
