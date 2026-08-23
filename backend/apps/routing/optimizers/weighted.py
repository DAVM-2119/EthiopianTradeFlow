from typing import List, Tuple
from .base import BaseRouteOptimizer
from apps.routing.providers.base import RouteCandidate

class WeightedRouteOptimizer(BaseRouteOptimizer):
    """
    Phase 16 deterministic weighted route optimizer.
    Normalizes candidates across Distance, Duration, Fuel, and Security Risk,
    then computes a weighted multi-attribute cost score:
    Score = (w_d * D_norm) + (w_t * T_norm) + (w_f * F_norm) + (w_r * R_norm)
    Lower score indicates a superior route.
    """
    WEIGHT_DISTANCE = 0.25
    WEIGHT_TIME = 0.25
    WEIGHT_FUEL = 0.30
    WEIGHT_RISK = 0.20

    def evaluate_candidates(self, candidates: List[RouteCandidate]) -> List[Tuple[RouteCandidate, float]]:
        if not candidates:
            return []

        if len(candidates) == 1:
            return [(candidates[0], 0.1000)]

        max_dist = max(c.distance_km for c in candidates) or 1.0
        max_dur = max(c.duration_minutes for c in candidates) or 1
        max_fuel = max(c.estimated_fuel_liters for c in candidates) or 1.0
        max_risk = max(c.risk_score for c in candidates) or 1.0

        evaluated: List[Tuple[RouteCandidate, float]] = []
        for c in candidates:
            d_norm = c.distance_km / max_dist
            t_norm = c.duration_minutes / max_dur
            f_norm = c.estimated_fuel_liters / max_fuel
            r_norm = c.risk_score / max_risk

            score = (
                (self.WEIGHT_DISTANCE * d_norm) +
                (self.WEIGHT_TIME * t_norm) +
                (self.WEIGHT_FUEL * f_norm) +
                (self.WEIGHT_RISK * r_norm)
            )
            score_val = round(float(score), 4)
            evaluated.append((c, score_val))

        evaluated.sort(key=lambda x: x[1])
        return evaluated
