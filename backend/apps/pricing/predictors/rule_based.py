from decimal import Decimal
from typing import Dict, Any
from .base import BasePricingEngine, PricingContext, PricingCalculationResult

class RuleBasedPricingEngine(BasePricingEngine):
    """
    Phase 15 rule-based deterministic pricing engine.
    Calculates spot rates based on distance, cargo weight, demand/capacity balance,
    fuel cost index, corridor congestion level, and floor/ceiling boundaries.
    """
    BASE_RATE_PER_KM_PER_TON = Decimal('2.50')  # 2.50 ETB per km per ton
    MINIMUM_BASE_PRICE = Decimal('5000.00')

    CONGESTION_MULTIPLIERS: Dict[str, Decimal] = {
        'LOW': Decimal('1.00'),
        'NORMAL': Decimal('1.05'),
        'HIGH': Decimal('1.15'),
        'SEVERE': Decimal('1.30'),
    }

    def calculate_price(self, context: PricingContext) -> PricingCalculationResult:
        dist = Decimal(str(round(max(context.distance_km, 1.0), 2)))
        weight = Decimal(str(round(max(context.weight_tons, 0.1), 2)))
        raw_base = dist * weight * self.BASE_RATE_PER_KM_PER_TON
        base_price = max(raw_base, self.MINIMUM_BASE_PRICE)

        loads = max(context.active_posted_loads, 1)
        vehicles = max(context.available_vehicles, 1)
        demand_capacity_ratio = loads / vehicles

        if demand_capacity_ratio < 0.75:
            demand_multiplier = Decimal('0.90')
        elif demand_capacity_ratio <= 1.25:
            demand_multiplier = Decimal('1.00')
        elif demand_capacity_ratio <= 1.75:
            demand_multiplier = Decimal('1.15')
        else:
            demand_multiplier = Decimal('1.30')

        ref_fuel = max(context.reference_fuel_price, 1.0)
        curr_fuel = max(context.current_fuel_price, 1.0)
        fuel_ratio = curr_fuel / ref_fuel
        fuel_multiplier = Decimal(str(round(min(max(fuel_ratio, 0.75), 1.50), 2)))

        cg_key = (context.congestion_level or 'NORMAL').strip().upper()
        congestion_multiplier = self.CONGESTION_MULTIPLIERS.get(cg_key, Decimal('1.05'))

        calculated_price = base_price * demand_multiplier * fuel_multiplier * congestion_multiplier
        calculated_price = Decimal(str(round(calculated_price, 2)))

        floor = context.pricing_floor if context.pricing_floor is not None else Decimal(str(round(base_price * Decimal('0.75'), 2)))
        ceiling = context.pricing_ceiling if context.pricing_ceiling is not None else Decimal(str(round(base_price * Decimal('2.50'), 2)))

        final_price = max(min(calculated_price, ceiling), floor)
        final_price = Decimal(str(round(final_price, 2)))

        input_snapshot = {
            "load_id": context.load_id,
            "origin_city": context.origin_city,
            "destination_city": context.destination_city,
            "distance_km": float(dist),
            "weight_tons": float(weight),
            "cargo_type": context.cargo_type,
            "active_posted_loads": context.active_posted_loads,
            "available_vehicles": context.available_vehicles,
            "demand_capacity_ratio": round(demand_capacity_ratio, 2),
            "current_fuel_price": context.current_fuel_price,
            "reference_fuel_price": context.reference_fuel_price,
            "congestion_level": cg_key,
            "floor": float(floor),
            "ceiling": float(ceiling),
        }

        output_snapshot = {
            "base_price": float(base_price),
            "demand_multiplier": float(demand_multiplier),
            "fuel_multiplier": float(fuel_multiplier),
            "congestion_multiplier": float(congestion_multiplier),
            "calculated_price": float(calculated_price),
            "final_price": float(final_price),
        }

        return PricingCalculationResult(
            base_price=base_price,
            demand_multiplier=demand_multiplier,
            fuel_multiplier=fuel_multiplier,
            congestion_multiplier=congestion_multiplier,
            calculated_price=calculated_price,
            final_price=final_price,
            pricing_method='RULE_BASED',
            algorithm_version='pricing-v1',
            input_snapshot=input_snapshot,
            output_snapshot=output_snapshot
        )
