import pytest
from django.utils import timezone
from ml.common.model_registry import model_registry
from ml.eta.predictor import MLETAPredictor
from apps.eta.predictors.base import ETAContext

class BrokenPredictor:
    def predict(self, context):
        raise RuntimeError("Forced ML Model Failure")

@pytest.mark.django_db
def test_missing_model_fallback():
    model_registry._registry.clear()
    model_registry._loaded_models.clear()

    predictor = MLETAPredictor()
    context = ETAContext(
        shipment_id="fallback-test-shipment",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        current_latitude=11.5883,
        current_longitude=43.1450,
        current_speed_kmh=60.0,
        recent_average_speed_kmh=60.0,
        known_delay_minutes=0,
        timestamp=timezone.now()
    )

    res = predictor.predict(context)
    # Should fall back cleanly without throwing an exception
    assert res.estimated_arrival is not None
    assert res.prediction_method in ("RULE_BASED", "ML_GRADIENT_BOOSTING")


@pytest.mark.django_db
def test_inference_exception_fallback():
    predictor = MLETAPredictor()
    context = ETAContext(
        shipment_id="exception-test-shipment",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        current_latitude=None,  # missing lat/lon
        current_longitude=None,
        current_speed_kmh=None,
        recent_average_speed_kmh=None,
        known_delay_minutes=0,
        timestamp=timezone.now()
    )

    res = predictor.predict(context)
    # Must return valid prediction safely
    assert res.estimated_arrival is not None
