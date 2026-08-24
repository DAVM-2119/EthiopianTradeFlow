import os
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml.common.model_metadata import ModelMetadata
from ml.common.model_registry import model_registry
from ml.data.dataset_builders import build_eta_training_dataset
from .features import FEATURE_COLUMNS

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')

def train_eta_model(dataset: pd.DataFrame = None, version: str = "eta-v1") -> dict:
    """
    Trains Scikit-Learn GradientBoostingRegressor model for ETA prediction on corridor data.
    Registers trained model and metadata artifacts into ml/artifacts/.
    """
    if dataset is None:
        dataset = build_eta_training_dataset(num_synthetic_samples=5000)

    X = dataset[FEATURE_COLUMNS]
    y = dataset['target_remaining_minutes']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    metrics = {
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'r2': round(r2, 4),
    }

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    model_path = os.path.join(ARTIFACTS_DIR, f"{version}.joblib")
    meta_path = os.path.join(ARTIFACTS_DIR, f"{version}.json")

    joblib.dump(model, model_path)

    metadata = ModelMetadata(
        model_name="eta",
        version=version,
        algorithm="GradientBoostingRegressor",
        feature_names=FEATURE_COLUMNS,
        target_name="target_remaining_minutes",
        metrics=metrics,
        description="Scikit-Learn Gradient Boosting Regressor for Djibouti-Modjo Highway ETA prediction.",
        is_active=True,
    )
    metadata.save_json(meta_path)

    # Register into in-memory ModelRegistry
    model_registry.register_model("eta", version, model, metadata, model_path)

    print(f"=== ETA ML Model Trained ({version}) ===")
    print(f"MAE: {mae:.2f} minutes | RMSE: {rmse:.2f} minutes | R² Score: {r2:.4f}")
    print(f"Artifacts saved to {model_path}")

    return {
        'model_path': model_path,
        'metadata_path': meta_path,
        'metrics': metrics,
    }
