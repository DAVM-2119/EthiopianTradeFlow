import pytest
from datetime import datetime, timedelta, timezone as py_tz
from decimal import Decimal
from apps.eta.predictors import ETAContext, RuleBasedETAPredictor

def test_rule_based_predictor_with_coordinates_and_speed():
    predictor = RuleBasedETAPredictor()
    now = datetime.now(py_tz.utc)

    context = ETAContext(
        shipment_id="shp-100",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        current_latitude=8.540,
        current_longitude=39.270,
        current_speed_kmh=60.0,
        recent_average_speed_kmh=60.0,
        known_delay_minutes=30,
        timestamp=now
    )

    res = predictor.predict(context)
    assert res.remaining_distance_km > Decimal('0.00')
    assert res.expected_speed_kmh == Decimal('60.00')
    assert res.delay_minutes == 30
    assert res.prediction_method == 'RULE_BASED'
    assert res.estimated_arrival > now


def test_rule_based_predictor_zero_speed_fallback():
    predictor = RuleBasedETAPredictor()
    now = datetime.now(py_tz.utc)

    context = ETAContext(
        shipment_id="shp-101",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        current_latitude=11.588,
        current_longitude=43.145,
        current_speed_kmh=0.0,
        recent_average_speed_kmh=0.0,
        known_delay_minutes=0,
        timestamp=now
    )

    res = predictor.predict(context)
    assert res.expected_speed_kmh == Decimal('50.00')
    assert res.remaining_distance_km > Decimal('500.00')
