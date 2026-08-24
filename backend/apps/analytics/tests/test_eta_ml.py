import pytest
from django.utils import timezone
from ml.data.synthetic_data import generate_synthetic_corridor_dataset
from ml.eta.train import train_eta_model
from ml.eta.evaluate import evaluate_eta_model
from ml.eta.predictor import MLETAPredictor
from apps.eta.predictors.base import ETAContext

@pytest.mark.django_db
def test_synthetic_data_generation():
    df = generate_synthetic_corridor_dataset(num_samples=100)
    assert len(df) == 100
    assert 'remaining_distance_km' in df.columns
    assert 'target_remaining_minutes' in df.columns


@pytest.mark.django_db
def test_train_and_predict_eta():
    train_res = train_eta_model(version="eta-pytest-v1")
    assert 'metrics' in train_res
    assert train_res['metrics']['mae'] > 0

    eval_res = evaluate_eta_model()
    assert 'ml_mae_minutes' in eval_res
    assert 'mae_improvement_pct' in eval_res

    predictor = MLETAPredictor()
    context = ETAContext(
        shipment_id="test-pytest-shipment",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        current_latitude=11.5883,
        current_longitude=43.1450,
        current_speed_kmh=65.0,
        recent_average_speed_kmh=60.0,
        known_delay_minutes=0,
        timestamp=timezone.now()
    )

    pred_res = predictor.predict(context)
    assert pred_res.prediction_method == "ML_GRADIENT_BOOSTING"
    assert pred_res.confidence > 0
    assert pred_res.estimated_arrival > context.timestamp
