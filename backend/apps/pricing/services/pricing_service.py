from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.marketplace.models import Load, LoadStatusChoices
from apps.fleet.models import Vehicle, VehicleStatusChoices
from apps.eta.predictors.rule_based import CITY_COORDINATES, DEFAULT_CORRIDOR_DISTANCES_KM, haversine_distance_km
from apps.pricing.models import PriceQuote, ContractRate, PricingAudit
from apps.pricing.predictors import PricingContext, RuleBasedPricingEngine
from apps.pricing.selectors import get_active_contract_rate
from apps.core.exceptions import NotFoundException

def calculate_and_save_price_quote(*, load_id, engine=None):
    """
    Calculates and persists a new PriceQuote and PricingAudit record for a load.
    Checks locked contract rates for spot rate divergence warnings (FR-04.2).
    Logs complete input/output snapshots for auditability (FR-04.3).
    """
    load = Load.objects.select_related('shipper').filter(id=load_id).first()
    if not load:
        raise NotFoundException("Load not found.")

    if engine is None:
        engine = RuleBasedPricingEngine()

    # 1. Estimate corridor distance
    orig_key = load.origin_city.strip().lower()
    dest_key = load.destination_city.strip().lower()
    orig_coords = CITY_COORDINATES.get(orig_key)
    dest_coords = CITY_COORDINATES.get(dest_key)

    if orig_coords and dest_coords:
        distance_km = haversine_distance_km(orig_coords[0], orig_coords[1], dest_coords[0], dest_coords[1])
    else:
        distance_km = DEFAULT_CORRIDOR_DISTANCES_KM.get((orig_key, dest_key)) or DEFAULT_CORRIDOR_DISTANCES_KM.get((dest_key, orig_key)) or 300.0

    # 2. Demand / Capacity counts
    active_posted_loads = Load.objects.filter(status=LoadStatusChoices.POSTED).count()
    available_vehicles = Vehicle.objects.filter(status=VehicleStatusChoices.AVAILABLE).count()

    now = timezone.now()
    context = PricingContext(
        load_id=str(load.id),
        origin_city=load.origin_city,
        destination_city=load.destination_city,
        distance_km=distance_km,
        weight_tons=float(load.weight),
        volume_cbm=float(load.volume) if load.volume else None,
        cargo_type=load.cargo_type,
        active_posted_loads=active_posted_loads,
        available_vehicles=available_vehicles,
        current_fuel_price=95.00,       # ETB per liter
        reference_fuel_price=90.00,     # Reference ETB per liter
        congestion_level='NORMAL',
        timestamp=now
    )

    res = engine.calculate_price(context)

    # 3. Contract Rate Divergence Check (FR-04.2)
    contract = get_active_contract_rate(load.shipper, load.origin_city, load.destination_city)
    divergence_warning = False
    divergence_notes = ""

    if contract:
        agreed_rate = contract.agreed_rate
        diff_percent = abs(res.final_price - agreed_rate) / agreed_rate * Decimal('100.00')
        if diff_percent > contract.divergence_threshold_percent:
            divergence_warning = True
            divergence_notes = f"Spot rate ({res.final_price} ETB) diverges from contract rate ({agreed_rate} ETB) by {diff_percent:.1f}%."

    # 4. Create PriceQuote
    price_quote = PriceQuote.objects.create(
        load=load,
        base_price=res.base_price,
        demand_multiplier=res.demand_multiplier,
        fuel_multiplier=res.fuel_multiplier,
        congestion_multiplier=res.congestion_multiplier,
        calculated_price=res.calculated_price,
        final_price=res.final_price,
        currency='ETB',
        pricing_method=res.pricing_method,
        algorithm_version=res.algorithm_version,
        valid_from=now,
        valid_until=now + timedelta(hours=24),
        divergence_warning=divergence_warning,
        divergence_notes=divergence_notes
    )

    # 5. Create PricingAudit Record (FR-04.3)
    PricingAudit.objects.create(
        price_quote=price_quote,
        input_snapshot=res.input_snapshot,
        output_snapshot=res.output_snapshot,
        algorithm_version=res.algorithm_version,
        calculation_reason="Dynamic spot rate calculation"
    )

    return price_quote
