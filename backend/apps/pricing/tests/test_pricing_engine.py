import pytest
from decimal import Decimal
from apps.pricing.predictors import PricingContext, RuleBasedPricingEngine

def test_pricing_engine_normal_demand_and_multipliers():
    engine = RuleBasedPricingEngine()
    context = PricingContext(
        load_id="load-100",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        distance_km=65.0,
        weight_tons=20.0,
        volume_cbm=40.0,
        cargo_type="GENERAL_CARGO",
        active_posted_loads=10,
        available_vehicles=10,
        current_fuel_price=90.0,
        reference_fuel_price=90.0,
        congestion_level="NORMAL"
    )

    res = engine.calculate_price(context)
    assert res.demand_multiplier == Decimal('1.00')
    assert res.fuel_multiplier == Decimal('1.00')
    assert res.congestion_multiplier == Decimal('1.05')
    assert res.final_price > Decimal('0.00')
    assert "demand_multiplier" in res.output_snapshot


def test_pricing_engine_surge_demand_and_floor_ceiling():
    engine = RuleBasedPricingEngine()
    context = PricingContext(
        load_id="load-101",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        distance_km=820.0,
        weight_tons=30.0,
        volume_cbm=60.0,
        cargo_type="CONTAINERIZED",
        active_posted_loads=100,
        available_vehicles=20,
        current_fuel_price=108.0,
        reference_fuel_price=90.0,
        congestion_level="HIGH",
        pricing_ceiling=Decimal("100000.00")
    )

    res = engine.calculate_price(context)
    assert res.demand_multiplier == Decimal('1.30')
    assert res.congestion_multiplier == Decimal('1.15')
    assert res.final_price <= Decimal("100000.00")
