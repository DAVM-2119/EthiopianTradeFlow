import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from ml.common.model_registry import model_registry
from ml.data.dataset_builders import build_eta_training_dataset
from .features import FEATURE_COLUMNS, extract_eta_features

def evaluate_eta_model(dataset: pd.DataFrame = None) -> dict:
    """
    Evaluates current active ML model vs deterministic rule-based benchmark on test dataset.
    """
    if dataset is None:
        dataset = build_eta_training_dataset(num_synthetic_samples=1000)

    reg_info = model_registry.get_active_model("eta")
    if not reg_info:
        return {'error': 'No active ML model found in registry.'}

    model = reg_info['model']
    metadata = reg_info['metadata']

    X_test = dataset[FEATURE_COLUMNS]
    y_true = dataset['target_remaining_minutes']

    ml_preds = model.predict(X_test)

    # Rule-based calculation benchmark: (distance / avg_speed) * 60 + incident_delay
    rule_preds = (dataset['remaining_distance_km'] / dataset['average_speed_kmh']) * 60.0 + (dataset['incident_count'] * 30.0)

    ml_mae = float(mean_absolute_error(y_true, ml_preds))
    rule_mae = float(mean_absolute_error(y_true, rule_preds))

    comparison = {
        'model_version': metadata.version,
        'algorithm': metadata.algorithm,
        'sample_count': len(dataset),
        'ml_mae_minutes': round(ml_mae, 2),
        'rule_based_mae_minutes': round(rule_mae, 2),
        'mae_improvement_pct': round(((rule_mae - ml_mae) / rule_mae) * 100.0, 2),
    }

    print("=== ETA Model Benchmark Evaluation ===")
    print(f"ML Model ({metadata.version}): MAE = {ml_mae:.2f} mins")
    print(f"Rule-Based Baseline:          MAE = {rule_mae:.2f} mins")
    print(f"Accuracy Improvement:          {comparison['mae_improvement_pct']}%")

    return comparison
