import pytest
from ml.common.base import PredictionResult
from ml.common.model_registry import ModelRegistry, model_registry
from ml.common.model_metadata import ModelMetadata
from ml.matching.ranker import AdvancedMatcher
from ml.optimization.route_optimizer import AdvancedRouteOptimizer

@pytest.mark.django_db
def test_prediction_result_structure():
    res = PredictionResult(
        prediction=42.0,
        algorithm="test_algo",
        model_version="v1.0",
        confidence=0.95,
        fallback_used=False
    )
    d = res.to_dict()
    assert d['prediction'] == 42.0
    assert d['algorithm'] == "test_algo"
    assert d['model_version'] == "v1.0"
    assert d['confidence'] == 0.95
    assert d['fallback_used'] is False


@pytest.mark.django_db
def test_model_registry_singleton():
    reg1 = ModelRegistry()
    reg2 = ModelRegistry()
    assert reg1 is reg2


@pytest.mark.django_db
def test_advanced_matcher():
    matcher = AdvancedMatcher()
    bids = [
        {'id': '1', 'amount': 5000, 'on_time_rate': 0.98, 'cancellation_rate': 0.01, 'corridor_trips': 40},
        {'id': '2', 'amount': 4500, 'on_time_rate': 0.85, 'cancellation_rate': 0.10, 'corridor_trips': 5},
    ]
    ranked = matcher.rank_bids({}, bids)
    assert len(ranked) == 2
    assert 'ml_composite_score' in ranked[0]
    assert ranked[0]['ml_composite_score'] >= ranked[1]['ml_composite_score']


@pytest.mark.django_db
def test_or_tools_route_optimizer():
    optimizer = AdvancedRouteOptimizer()
    matrix = [
        [0, 10, 20],
        [10, 0, 15],
        [20, 15, 0],
    ]
    res = optimizer.optimize_route_waypoints(matrix, depot_index=0)
    assert 'route' in res
    assert 'total_distance_km' in res
    assert res['status'] in ('OPTIMAL_OR_TOOLS', 'FALLBACK')
