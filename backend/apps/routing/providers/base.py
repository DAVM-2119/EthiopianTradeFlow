from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class RouteLegCandidate:
    sequence: int
    start_point: str
    end_point: str
    distance_km: float
    duration_minutes: int
    estimated_fuel_liters: float
    security_risk_score: float = 0.10


@dataclass
class RouteCandidate:
    provider: str
    provider_route_id: str
    origin_city: str
    destination_city: str
    distance_km: float
    duration_minutes: int
    estimated_fuel_liters: float
    estimated_fuel_cost: float
    risk_score: float = 0.10
    legs: List[RouteLegCandidate] = field(default_factory=list)
    geometry_json: Dict[str, Any] = field(default_factory=dict)


class BaseRoutingProvider:
    """
    Abstract interface for routing engine providers (OSRM, GraphHopper, Geodesic Fallback, etc.).
    """
    def calculate_candidate_routes(
        self,
        origin_city: str,
        destination_city: str,
        origin_lat: Optional[float] = None,
        origin_lon: Optional[float] = None,
        dest_lat: Optional[float] = None,
        dest_lon: Optional[float] = None
    ) -> List[RouteCandidate]:
        raise NotImplementedError("Subclasses must implement calculate_candidate_routes()")
