from decimal import Decimal
from typing import Optional
from django.contrib.gis.geos import Point
from django.utils import timezone
from apps.core.exceptions import NotFoundException, ValidationException
from apps.risk.models import IncidentReport, IncidentTypeChoices, IncidentStatusChoices, RiskSeverityChoices

def report_incident(
    *,
    reported_by,
    incident_type: str,
    description: str,
    latitude: Decimal,
    longitude: Decimal,
    shipment_id = None,
    driver = None,
    severity: str = RiskSeverityChoices.MEDIUM
) -> IncidentReport:
    """
    Submits a new incident report.
    """
    if incident_type not in IncidentTypeChoices.values:
        raise ValidationException(f"Invalid incident_type: {incident_type}")

    if latitude < Decimal('-90.0') or latitude > Decimal('90.0'):
        raise ValidationException("Latitude must be between -90 and 90.")
    if longitude < Decimal('-180.0') or longitude > Decimal('180.0'):
        raise ValidationException("Longitude must be between -180 and 180.")

    point = Point(float(longitude), float(latitude), srid=4326)

    incident = IncidentReport.objects.create(
        reported_by=reported_by,
        shipment_id=shipment_id,
        driver=driver,
        incident_type=incident_type,
        description=description,
        location=point,
        latitude=latitude,
        longitude=longitude,
        severity=severity,
        status=IncidentStatusChoices.REPORTED
    )
    return incident


def verify_incident(incident_id, *, verified_by, notes: str = "", status: str = IncidentStatusChoices.VERIFIED) -> IncidentReport:
    """
    Verifies or updates status of an incident report (Admin / Staff).
    """
    incident = IncidentReport.objects.filter(id=incident_id).first()
    if not incident:
        raise NotFoundException("IncidentReport not found.")

    incident.status = status
    incident.verification_notes = notes
    incident.verified_by = verified_by
    incident.save()
    return incident
