from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FuelRecommendation:
    category: str
    title: str
    severity: str
    message: str
    actionable_advice: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseFuelAnalyzer:
    """
    Abstract interface for fuel consumption analyzers (rule-based, historical, ML).
    """
    def analyze_vehicle_efficiency(self, vehicle_id: str) -> List[FuelRecommendation]:
        raise NotImplementedError("Subclasses must implement analyze_vehicle_efficiency()")

    def analyze_driver_efficiency(self, driver_id: str) -> List[FuelRecommendation]:
        raise NotImplementedError("Subclasses must implement analyze_driver_efficiency()")
