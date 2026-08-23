import math
from datetime import timedelta
from decimal import Decimal
from typing import Tuple

from .base import BaseETAPredictor, ETAContext, ETAPredictionResult

CITY_COORDINATES = {
    'djibouti port': (11.588, 43.145),
    'djibouti': (11.588, 43.145),
    'modjo': (8.590, 39.120),
    'modjo dry port': (8.590, 39.120),
    'addis ababa': (9.0054, 38.7578),
    'adama': (8.540, 39.270),
    'awash': (8.983, 40.167),
    'dire dawa': (9.600, 41.866),
    'hawassa': (7.062, 38.476),
    'mekelle': (13.496, 39.475),
    'kombolcha': (11.083, 39.733),
    'bahir dar': (11.593, 37.390),
    'jimma': (7.673, 36.834),
}

DEFAULT_CORRIDOR_DISTANCES_KM = {
    ('djibouti port', 'modjo'): 820.0,
    ('djibouti port', 'addis ababa'): 865.0,
    ('modjo', 'addis ababa'): 65.0,
    ('addis ababa', 'hawassa'): 275.0,
    ('addis ababa', 'dire dawa'): 450.0,
    ('addis ababa', 'mekelle'): 780.0,
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates geodesic distance in kilometers between two GPS coordinates using Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class RuleBasedETAPredictor(BaseETAPredictor):
    """
    Phase 14 rule-based baseline ETA predictor.
    Calculates predicted arrival using current GPS position, destination geodesic distance,
    corridor speed heuristics, and accumulated delay inputs.
    """
    DEFAULT_SPEED_KMH = 50.0

    def predict(self, context: ETAContext) -> ETAPredictionResult:
        # 1. Determine destination coordinates
        dest_key = context.destination_city.strip().lower()
        dest_coords = CITY_COORDINATES.get(dest_key)

        remaining_distance = Decimal('0.00')

        if context.current_latitude is not None and context.current_longitude is not None and dest_coords:
            calc_dist = haversine_distance_km(
                context.current_latitude,
                context.current_longitude,
                dest_coords[0],
                dest_coords[1]
            )
            remaining_distance = Decimal(str(round(calc_dist, 2)))
        else:
            # Fallback to corridor lookup table
            orig_key = context.origin_city.strip().lower()
            dist_km = DEFAULT_CORRIDOR_DISTANCES_KM.get((orig_key, dest_key)) or DEFAULT_CORRIDOR_DISTANCES_KM.get((dest_key, orig_key)) or 300.0
            remaining_distance = Decimal(str(round(dist_km, 2)))

        # Ensure non-negative distance
        remaining_distance = max(remaining_distance, Decimal('0.00'))

        # 2. Determine expected speed
        expected_speed = Decimal(str(self.DEFAULT_SPEED_KMH))
        if context.recent_average_speed_kmh is not None and context.recent_average_speed_kmh > 5.0:
            expected_speed = Decimal(str(round(min(context.recent_average_speed_kmh, 90.0), 2)))
        elif context.current_speed_kmh is not None and context.current_speed_kmh > 5.0:
            expected_speed = Decimal(str(round(min(context.current_speed_kmh, 90.0), 2)))

        # 3. Calculate remaining travel time & apply delays
        travel_time_hours = float(remaining_distance) / float(expected_speed)
        travel_time_minutes = travel_time_hours * 60.0
        total_minutes = travel_time_minutes + float(context.known_delay_minutes)

        estimated_arrival = context.timestamp + timedelta(minutes=round(total_minutes))

        return ETAPredictionResult(
            estimated_arrival=estimated_arrival,
            remaining_distance_km=remaining_distance,
            expected_speed_kmh=expected_speed,
            delay_minutes=max(context.known_delay_minutes, 0),
            prediction_method='RULE_BASED',
            algorithm_version='eta-v1',
            confidence=Decimal('0.85')
        )
