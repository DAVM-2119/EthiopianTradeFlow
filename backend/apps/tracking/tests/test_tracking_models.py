import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.contrib.gis.geos import Point

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent

@pytest.mark.django_db
def test_tracking_event_model_creation_and_pointfield():
    shipper = User.objects.create_user(email='shipper_tm@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_tm@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_tm@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Tracking Model Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("40000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    lat = Decimal("9.005400")
    lon = Decimal("38.757800")
    point = Point(float(lon), float(lat), srid=4326)

    event = TrackingEvent.objects.create(
        event_id="evt-unique-101",
        shipment=shipment,
        driver=driver,
        location=point,
        latitude=lat,
        longitude=lon,
        speed=Decimal("65.50"),
        heading=Decimal("90.00"),
        recorded_at=now
    )

    assert event.event_id == "evt-unique-101"
    assert event.shipment == shipment
    assert event.driver == driver
    assert event.latitude == lat
    assert event.longitude == lon
    assert event.location.x == float(lon)
    assert event.location.y == float(lat)
