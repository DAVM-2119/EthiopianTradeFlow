from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class ETAContext:
    shipment_id: str
    origin_city: str
    destination_city: str
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    current_speed_kmh: Optional[float]
    recent_average_speed_kmh: Optional[float]
    known_delay_minutes: int
    timestamp: datetime


@dataclass
class ETAPredictionResult:
    estimated_arrival: datetime
    remaining_distance_km: Decimal
    expected_speed_kmh: Decimal
    delay_minutes: int
    prediction_method: str
    algorithm_version: str
    confidence: Decimal


class BaseETAPredictor:
    """
    Abstract interface for ETA prediction engine.
    Ensures seamless pluggability between RuleBasedETAPredictor (Phase 14) and MLETA Predictor (Phase 25).
    """
    def predict(self, context: ETAContext) -> ETAPredictionResult:
        raise NotImplementedError("Subclasses must implement predict()")
