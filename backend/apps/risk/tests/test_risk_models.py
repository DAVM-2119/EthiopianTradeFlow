import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.risk.models import (
    RiskZone, RiskSeverityChoices, RiskZoneSourceChoices,
    IncidentReport, IncidentTypeChoices, IncidentStatusChoices,
    SecurityAlert, AlertTypeChoices, AlertStatusChoices
)

@pytest.mark.django_db
def test_create_risk_zone_model():
    admin_user = User.objects.create_user(email='admin_risk_m@tradeflow.et', password='Password123!', role=RoleChoices.ADMIN)
    zone = RiskZone.objects.create(
        name="Afar Border Corridor",
        description="High security risk advisory",
        latitude=Decimal("11.500000"),
        longitude=Decimal("41.200000"),
        radius_km=Decimal("15.00"),
        severity=RiskSeverityChoices.HIGH,
        source=RiskZoneSourceChoices.GOVERNMENT_ADVISORY,
        created_by=admin_user
    )

    assert zone.name == "Afar Border Corridor"
    assert zone.is_active is True
    assert zone.is_currently_effective is True
    assert "RiskZone:" in str(zone)


@pytest.mark.django_db
def test_create_incident_report_and_security_alert_models():
    shipper = User.objects.create_user(email='shipper_risk_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter_user = User.objects.create_user(email='transporter_risk_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_profile, _ = TransporterProfile.objects.get_or_create(user=transporter_user, defaults={'business_name': 'Transporter Risk M'})
    driver = User.objects.create_user(email='driver_risk_m@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    now = timezone.now()

    vehicle = Vehicle.objects.create(
        transporter=t_profile, registration_number="ETH-RZ-001", vehicle_type="HEAVY_TRUCK", capacity=Decimal("30.00")
    )
    load = Load.objects.create(
        shipper=shipper, title="Risk Model Load", origin_city="Djibouti Port", destination_city="Modjo",
        weight=Decimal("30.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1), pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter_user, amount=Decimal("80000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(
        load=load, bid=bid, shipper=shipper, transporter=transporter_user, vehicle=vehicle, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT
    )

    incident = IncidentReport.objects.create(
        reported_by=driver,
        shipment=shipment,
        driver=driver,
        incident_type=IncidentTypeChoices.CHECKPOINT_DELAY,
        description="Heavy customs audit checkpoint congestion",
        latitude=Decimal("8.540000"),
        longitude=Decimal("39.270000"),
        severity=RiskSeverityChoices.MEDIUM,
        status=IncidentStatusChoices.REPORTED
    )
    assert incident.incident_type == IncidentTypeChoices.CHECKPOINT_DELAY
    assert "Incident:" in str(incident)

    alert = SecurityAlert.objects.create(
        shipment=shipment,
        driver=driver,
        incident=incident,
        alert_type=AlertTypeChoices.INCIDENT_IN_PROXIMITY,
        severity=RiskSeverityChoices.MEDIUM,
        distance_at_detection_km=Decimal("4.50"),
        message="Checkpoint delay ahead",
        status=AlertStatusChoices.ACTIVE
    )
    assert alert.shipment == shipment
    assert alert.status == AlertStatusChoices.ACTIVE
    assert "SecurityAlert:" in str(alert)
