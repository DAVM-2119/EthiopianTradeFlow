from datetime import timedelta
from decimal import Decimal
from typing import Optional

from apps.eta.predictors.base import BaseETAPredictor, ETAContext, ETAPredictionResult
from apps.eta.predictors.rule_based import RuleBasedETAPredictor
from ml.common.model_registry import model_registry
from .features import extract_eta_features

class MLETAPredictor(BaseETAPredictor):
    """
    ML-capable ETA predictor using GradientBoostingRegressor model.
    Implements BaseETAPredictor interface with safe fallback to RuleBasedETAPredictor.
    """
    def __init__(self, fallback_predictor: Optional[BaseETAPredictor] = None):
        self.fallback_predictor = fallback_predictor or RuleBasedETAPredictor()

    def predict(self, context: ETAContext) -> ETAPredictionResult:
        try:
            reg_info = model_registry.get_active_model("eta")
            if not reg_info or not reg_info.get('model'):
                # ML model unavailable -> Fallback safely to RuleBasedETAPredictor
                return self.fallback_predictor.predict(context)

            model = reg_info['model']
            metadata = reg_info['metadata']

            # Extract features from context
            rule_res = self.fallback_predictor.predict(context)
            feature_dict = {
                'remaining_distance_km': float(rule_res.remaining_distance_km),
                'cargo_weight_tons': 30.0,
                'vehicle_type': 2.0,
                'hour_of_day': float(context.timestamp.hour),
                'day_of_week': float(context.timestamp.weekday()),
                'incident_count': float(context.known_delay_minutes // 30),
                'security_risk_level': 0.0,
                'average_speed_kmh': float(rule_res.expected_speed_kmh),
            }

            X = extract_eta_features(feature_dict)
            predicted_minutes = float(model.predict(X)[0])
            predicted_minutes = max(10.0, predicted_minutes)

            estimated_arrival = context.timestamp + timedelta(minutes=predicted_minutes)

            return ETAPredictionResult(
                estimated_arrival=estimated_arrival,
                remaining_distance_km=rule_res.remaining_distance_km,
                expected_speed_kmh=rule_res.expected_speed_kmh,
                delay_minutes=context.known_delay_minutes,
                prediction_method="ML_GRADIENT_BOOSTING",
                algorithm_version=metadata.version,
                confidence=Decimal('0.88')
            )
        except Exception as e:
            # On any ML inference exception, guarantee fallback without crashing tracking
            print(f"[MLETAPredictor] Inference exception fallback: {e}")
            return self.fallback_predictor.predict(context)
