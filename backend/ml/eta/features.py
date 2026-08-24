import numpy as np

FEATURE_COLUMNS = [
    'remaining_distance_km',
    'cargo_weight_tons',
    'vehicle_type',
    'hour_of_day',
    'day_of_week',
    'incident_count',
    'security_risk_level',
    'average_speed_kmh',
]

FEATURE_DEFAULTS = {
    'remaining_distance_km': 450.0,
    'cargo_weight_tons': 30.0,
    'vehicle_type': 2.0,
    'hour_of_day': 12.0,
    'day_of_week': 2.0,
    'incident_count': 0.0,
    'security_risk_level': 0.0,
    'average_speed_kmh': 60.0,
}

def extract_eta_features(context_dict: dict) -> np.ndarray:
    """
    Transforms an ETAContext or feature dictionary into a 2D numpy array suitable for Scikit-Learn prediction.
    """
    row = []
    for col in FEATURE_COLUMNS:
        val = context_dict.get(col)
        if val is None or val == '':
            val = FEATURE_DEFAULTS.get(col, 0.0)
        row.append(float(val))
    return np.array([row])
