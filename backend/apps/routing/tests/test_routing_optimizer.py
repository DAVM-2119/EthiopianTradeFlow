import pytest
from apps.routing.providers import RouteCandidate, RouteLegCandidate
from apps.routing.optimizers import WeightedRouteOptimizer

def test_weighted_route_optimizer():
    optimizer = WeightedRouteOptimizer()
    
    r1 = RouteCandidate(
        provider='OSRM', provider_route_id='rt-1', origin_city='Addis Ababa', destination_city='Modjo',
        distance_km=65.0, duration_minutes=70, estimated_fuel_liters=22.0, estimated_fuel_cost=1980.0, risk_score=0.20
    )
    r2 = RouteCandidate(
        provider='OSRM', provider_route_id='rt-2', origin_city='Addis Ababa', destination_city='Modjo',
        distance_km=70.0, duration_minutes=60, estimated_fuel_liters=21.0, estimated_fuel_cost=1890.0, risk_score=0.05
    )

    evaluated = optimizer.evaluate_candidates([r1, r2])
    assert len(evaluated) == 2
    best_candidate, best_score = evaluated[0]
    assert best_score <= evaluated[1][1]
    assert best_candidate in (r1, r2)
