from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import NotFoundException, ValidationException
from apps.shipments.models import Shipment
from apps.routing.models import Route, RouteStatusChoices
from apps.risk.models import (
    RiskZone, RiskSeverityChoices, RiskZoneSourceChoices,
    SecurityAlert, AlertTypeChoices, AlertStatusChoices
)
from apps.risk.selectors import (
    calculate_haversine_distance_km,
    get_active_risk_zones,
    get_active_incidents
)

def create_risk_zone(
    *,
    name: str,
    latitude: Decimal,
    longitude: Decimal,
    radius_km: Decimal = Decimal('10.00'),
    severity: str = RiskSeverityChoices.HIGH,
    source: str = RiskZoneSourceChoices.ADMIN,
    description: str = "",
    effective_from = None,
    effective_until = None,
    created_by = None
) -> RiskZone:
    """
    Creates a new geographic risk zone.
    """
    if latitude < Decimal('-90.0') or latitude > Decimal('90.0'):
        raise ValidationException("Latitude must be between -90 and 90.")
    if longitude < Decimal('-180.0') or longitude > Decimal('180.0'):
        raise ValidationException("Longitude must be between -180 and 180.")
    if radius_km <= Decimal('0.00'):
        raise ValidationException("Radius must be greater than zero.")

    point = Point(float(longitude), float(latitude), srid=4326)

    zone = RiskZone.objects.create(
        name=name,
        description=description,
        location=point,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        severity=severity,
        source=source,
        effective_from=effective_from or timezone.now(),
        effective_until=effective_until,
        created_by=created_by,
        verified_at=timezone.now() if source == RiskZoneSourceChoices.ADMIN else None
    )
    return zone


def update_risk_zone(zone_id, **kwargs) -> RiskZone:
    """
    Updates an existing risk zone.
    """
    zone = RiskZone.objects.filter(id=zone_id).first()
    if not zone:
        raise NotFoundException("RiskZone not found.")

    for field, value in kwargs.items():
        if hasattr(zone, field) and value is not None:
            setattr(zone, field, value)

    if 'latitude' in kwargs or 'longitude' in kwargs:
        lat = kwargs.get('latitude', zone.latitude)
        lon = kwargs.get('longitude', zone.longitude)
        if lat is not None and lon is not None:
            zone.location = Point(float(lon), float(lat), srid=4326)

    zone.save()
    return zone


def check_location_for_risk(
    *,
    shipment_id,
    latitude: Decimal,
    longitude: Decimal,
    driver_id = None
) -> Dict[str, Any]:
    """
    FR-08.2 Geographic risk detection algorithm.
    Checks coordinates against active RiskZone radius and active IncidentReport proximity.
    Generates SecurityAlert records with strict duplicate alert prevention.
    """
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    driver = shipment.driver if not driver_id else None

    lat_f = float(latitude)
    lon_f = float(longitude)

    active_zones = list(get_active_risk_zones())
    generated_alerts: List[SecurityAlert] = []
    detected_zones = []

    # Check routing boundary for alternate route suggestion
    alt_route = Route.objects.filter(
        shipment=shipment,
        status__in=[RouteStatusChoices.REROUTE_PROPOSED, RouteStatusChoices.ROUTE_ACTIVE]
    ).exclude(status=RouteStatusChoices.INACTIVE).first()
    alt_route_id = alt_route.id if alt_route else None

    with transaction.atomic():
        for zone in active_zones:
            if zone.latitude is None or zone.longitude is None:
                continue

            dist = calculate_haversine_distance_km(lat_f, lon_f, float(zone.latitude), float(zone.longitude))
            radius = float(zone.radius_km)

            if dist <= radius:
                detected_zones.append({
                    "zone_id": str(zone.id),
                    "name": zone.name,
                    "severity": zone.severity,
                    "distance_km": round(dist, 2),
                    "radius_km": radius
                })

                # Prevent Duplicate Alerts for same shipment & risk zone while an alert is ACTIVE
                existing_alert = SecurityAlert.objects.filter(
                    shipment=shipment,
                    risk_zone=zone,
                    status=AlertStatusChoices.ACTIVE
                ).first()

                if not existing_alert:
                    msg = f"Approaching high-risk zone '{zone.name}' (Severity: {zone.get_severity_display()}). Current distance: {dist:.2f} km."
                    action = "Review route selection. Slow down and maintain high vigilance or confirm alternative corridor route."

                    alert = SecurityAlert.objects.create(
                        shipment=shipment,
                        driver=driver or shipment.driver,
                        risk_zone=zone,
                        alert_type=AlertTypeChoices.APPROACHING_RISK_ZONE,
                        severity=zone.severity,
                        distance_at_detection_km=Decimal(str(round(dist, 2))),
                        message=msg,
                        suggested_action=action,
                        suggested_alternate_route_id=alt_route_id,
                        status=AlertStatusChoices.ACTIVE
                    )
                    generated_alerts.append(alert)

        # Proximity Check for Verified / Active Incidents (within 15 km)
        nearby_incidents = get_active_incidents(latitude=latitude, longitude=longitude, radius_km=15.0)
        for inc in nearby_incidents:
            dist = calculate_haversine_distance_km(lat_f, lon_f, float(inc.latitude), float(inc.longitude))

            existing_inc_alert = SecurityAlert.objects.filter(
                shipment=shipment,
                incident=inc,
                status=AlertStatusChoices.ACTIVE
            ).first()

            if not existing_inc_alert:
                msg = f"Active incident '{inc.get_incident_type_display()}' reported {dist:.2f} km ahead."
                action = "Prepare for potential delays or follow checkpoint reroute guidance."

                alert = SecurityAlert.objects.create(
                    shipment=shipment,
                    driver=driver or shipment.driver,
                    incident=inc,
                    alert_type=AlertTypeChoices.INCIDENT_IN_PROXIMITY,
                    severity=inc.severity,
                    distance_at_detection_km=Decimal(str(round(dist, 2))),
                    message=msg,
                    suggested_action=action,
                    suggested_alternate_route_id=alt_route_id,
                    status=AlertStatusChoices.ACTIVE
                )
                generated_alerts.append(alert)

    return {
        "shipment_id": str(shipment.id),
        "checked_at": timezone.now().isoformat(),
        "risk_detected": len(detected_zones) > 0 or len(generated_alerts) > 0,
        "detected_zones": detected_zones,
        "new_alerts_count": len(generated_alerts),
        "generated_alerts": generated_alerts
    }
