from typing import List, Tuple
from apps.routing.providers.base import RouteCandidate

class BaseRouteOptimizer:
    """
    Abstract interface for route optimization algorithms.
    """
    def evaluate_candidates(self, candidates: List[RouteCandidate]) -> List[Tuple[RouteCandidate, float]]:
        raise NotImplementedError("Subclasses must implement evaluate_candidates()")
