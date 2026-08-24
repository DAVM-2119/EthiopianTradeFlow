from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

@dataclass
class PredictionResult:
    """
    Standardized result wrapper returned by all TradeFlow ML predictors.
    Includes prediction payload and full operational metadata.
    """
    prediction: Any
    algorithm: str
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    fallback_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'prediction': str(self.prediction) if isinstance(self.prediction, datetime) else self.prediction,
            'algorithm': self.algorithm,
            'model_version': self.model_version,
            'confidence': float(self.confidence) if self.confidence is not None else None,
            'fallback_used': self.fallback_used,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
        }


class BasePredictor:
    """
    Abstract Base Class for all ML & optimization predictors.
    """
    def predict(self, features: Any) -> PredictionResult:
        raise NotImplementedError("Subclasses must implement predict()")
