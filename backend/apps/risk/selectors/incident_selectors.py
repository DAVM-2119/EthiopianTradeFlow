from decimal import Decimal
from apps.risk.models import IncidentReport, IncidentStatusChoices
from .risk_selectors import calculate_haversine_distance_km

def get_incidents_for_shipment(shipment_id):
    """
    Retrieves incident reports associated with a shipment.
    """
    return IncidentReport.objects.filter(shipment_id=shipment_id).select_related('reported_by', 'driver', 'verified_by').order_by('-reported_at')


def get_active_incidents(latitude=None, longitude=None, radius_km: float = 25.0):
    """
    Retrieves active/verified incidents, optionally filtered by coordinate proximity.
    """
    qs = IncidentReport.objects.filter(
        status__in=[IncidentStatusChoices.REPORTED, IncidentStatusChoices.UNDER_REVIEW, IncidentStatusChoices.VERIFIED]
    ).select_related('reported_by', 'shipment', 'driver').order_by('-reported_at')

    if latitude is None or longitude is None:
        return list(qs)

    lat_f = float(latitude)
    lon_f = float(longitude)

    results = []
    for inc in qs:
        dist = calculate_haversine_distance_km(lat_f, lon_f, float(inc.latitude), float(inc.longitude))
        if dist <= radius_km:
            results.append((inc, round(dist, 2)))

    results.sort(key=lambda item: item[1])
    return [item[0] for item in results]
