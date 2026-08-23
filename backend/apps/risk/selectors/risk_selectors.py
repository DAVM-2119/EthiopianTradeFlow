from decimal import Decimal
from math import radians, cos, sin, asin, sqrt
from django.utils import timezone
from django.db.models import Q
from apps.risk.models import RiskZone

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes geodesic distance between two lat/lon points using the Haversine formula.
    """
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return r * c


def get_active_risk_zones():
    """
    Retrieves all currently active and temporally valid risk zones.
    """
    now = timezone.now()
    return RiskZone.objects.filter(
        is_active=True,
        effective_from__lte=now
    ).filter(
        Q(effective_until__isnull=True) | Q(effective_until__gte=now)
    ).order_by('-severity', '-created_at')


def get_risk_zones_in_proximity(latitude: Decimal, longitude: Decimal, max_distance_km: float = 50.0):
    """
    Evaluates active risk zones within max_distance_km of given coordinates.
    """
    lat_f = float(latitude)
    lon_f = float(longitude)
    active_zones = list(get_active_risk_zones())

    results = []
    for zone in active_zones:
        if zone.latitude is not None and zone.longitude is not None:
            dist = calculate_haversine_distance_km(lat_f, lon_f, float(zone.latitude), float(zone.longitude))
            if dist <= max_distance_km:
                results.append((zone, round(dist, 2)))

    results.sort(key=lambda item: item[1])
    return results
