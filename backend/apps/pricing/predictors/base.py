from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

@dataclass
class PricingContext:
    load_id: str
    origin_city: str
    destination_city: str
    distance_km: float
    weight_tons: float
    volume_cbm: Optional[float]
    cargo_type: str
    active_posted_loads: int
    available_vehicles: int
    current_fuel_price: float
    reference_fuel_price: float
    congestion_level: str  # LOW, NORMAL, HIGH, SEVERE
    pricing_floor: Optional[Decimal] = None
    pricing_ceiling: Optional[Decimal] = None
    timestamp: Optional[datetime] = None


@dataclass
class PricingCalculationResult:
    base_price: Decimal
    demand_multiplier: Decimal
    fuel_multiplier: Decimal
    congestion_multiplier: Decimal
    calculated_price: Decimal
    final_price: Decimal
    pricing_method: str
    algorithm_version: str
    input_snapshot: Dict[str, Any] = field(default_factory=dict)
    output_snapshot: Dict[str, Any] = field(default_factory=dict)


class BasePricingEngine:
    """
    Abstract interface for pricing calculation engine.
    Ensures seamless pluggability between RuleBasedPricingEngine (Phase 15) and MLPricingEngine (Phase 25).
    """
    def calculate_price(self, context: PricingContext) -> PricingCalculationResult:
        raise NotImplementedError("Subclasses must implement calculate_price()")
