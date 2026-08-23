import pytest
from apps.routing.providers import OSRMRoutingProvider

def test_osrm_provider_candidate_generation():
    provider = OSRMRoutingProvider()
    candidates = provider.calculate_candidate_routes(
        origin_city="Djibouti Port",
        destination_city="Modjo"
    )

    assert len(candidates) >= 1
    c1 = candidates[0]
    assert c1.origin_city == "Djibouti Port"
    assert c1.destination_city == "Modjo"
    assert c1.distance_km > 500.0
    assert c1.duration_minutes > 0
    assert c1.estimated_fuel_liters > 0
    assert len(c1.legs) == 1
