import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.risk.models import RiskZone, SecurityAlert, AlertStatusChoices
from apps.risk.services import create_risk_zone, check_location_for_risk, report_incident, verify_incident, acknowledge_alert

@pytest.mark.django_db
def test_risk_location_check_and_duplicate_suppression():
    shipper = User.objects.create_user(email='shipper_risk_s@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_risk_s@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Risk S'})
    driver = User.objects.create_user(email='driver_risk_s@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile, registration_number="ETH-RZ-002", vehicle_type="HEAVY_TRUCK", capacity=Decimal("30.00")
    )
    load = Load.objects.create(
        shipper=shipper, title="Risk Service Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("85000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    zone = create_risk_zone(
        name="Awash Conflict Corridor",
        latitude=Decimal("8.540000"),
        longitude=Decimal("39.270000"),
        radius_km=Decimal("10.00"),
        severity="HIGH"
    )

    res1 = check_location_for_risk(
        shipment_id=shipment.id,
        latitude=Decimal("8.520000"),
        longitude=Decimal("39.260000"),
        driver_id=driver.id
    )

    assert res1['risk_detected'] is True
    assert res1['new_alerts_count'] == 1
    alert = res1['generated_alerts'][0]
    assert alert.risk_zone == zone
    assert alert.status == AlertStatusChoices.ACTIVE

    res2 = check_location_for_risk(
        shipment_id=shipment.id,
        latitude=Decimal("8.510000"),
        longitude=Decimal("39.250000"),
        driver_id=driver.id
    )

    assert res2['new_alerts_count'] == 0
    assert SecurityAlert.objects.filter(shipment=shipment, risk_zone=zone).count() == 1

    ack_alert = acknowledge_alert(alert.id, user=driver)
    assert ack_alert.status == AlertStatusChoices.ACKNOWLEDGED
