from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.db import transaction
from apps.shipments.models import Shipment
from apps.routing.models import Route, RouteStatusChoices
from apps.analytics.models import TripFuelRecord, FuelDataSourceChoices
from apps.analytics.analyzers import RuleBasedFuelAnalyzer
from apps.core.exceptions import NotFoundException, ValidationException

def calculate_fuel_efficiency_and_variance(
    *,
    distance_km: Decimal,
    estimated_fuel_liters: Decimal,
    actual_fuel_liters: Optional[Decimal] = None
) -> Dict[str, Optional[Decimal]]:
    """
    Zero-safe deterministic fuel calculation logic.
    """
    if distance_km <= Decimal('0.00'):
        raise ValidationException("Distance must be greater than zero.")
    if estimated_fuel_liters <= Decimal('0.00'):
        raise ValidationException("Estimated fuel liters must be greater than zero.")

    if actual_fuel_liters is not None and actual_fuel_liters > Decimal('0.00'):
        eff = round(distance_km / actual_fuel_liters, 2)
        var_liters = round(actual_fuel_liters - estimated_fuel_liters, 2)
        var_pct = round(((actual_fuel_liters - estimated_fuel_liters) / estimated_fuel_liters) * Decimal('100.00'), 2)
    else:
        eff = round(distance_km / estimated_fuel_liters, 2)
        var_liters = None
        var_pct = None

    return {
        "fuel_efficiency": eff,
        "fuel_variance_liters": var_liters,
        "fuel_variance_percentage": var_pct,
    }


def record_trip_fuel(
    *,
    shipment_id,
    actual_fuel_liters: Optional[Decimal] = None,
    distance_km: Optional[Decimal] = None,
    estimated_fuel_liters: Optional[Decimal] = None,
    data_source: str = FuelDataSourceChoices.MANUAL,
    notes: str = ""
) -> TripFuelRecord:
    """
    FR-07.1 Records or updates fuel consumption record for a shipment.
    Pulls distance and estimated fuel from active Route if not explicitly provided.
    """
    shipment = Shipment.objects.select_related('vehicle', 'driver', 'load').filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    if not shipment.vehicle:
        raise ValidationException("Shipment has no assigned vehicle.")

    if distance_km is None or estimated_fuel_liters is None:
        active_route = Route.objects.filter(shipment=shipment, status=RouteStatusChoices.ROUTE_ACTIVE).first()
        if active_route:
            if distance_km is None:
                distance_km = active_route.distance_km
            if estimated_fuel_liters is None:
                estimated_fuel_liters = active_route.estimated_fuel_liters

    if distance_km is None or distance_km <= Decimal('0.00'):
        distance_km = Decimal('300.00')
    if estimated_fuel_liters is None or estimated_fuel_liters <= Decimal('0.00'):
        estimated_fuel_liters = round(distance_km * Decimal('0.35'), 2)

    calcs = calculate_fuel_efficiency_and_variance(
        distance_km=distance_km,
        estimated_fuel_liters=estimated_fuel_liters,
        actual_fuel_liters=actual_fuel_liters
    )

    with transaction.atomic():
        record, created = TripFuelRecord.objects.update_or_create(
            shipment=shipment,
            defaults={
                'vehicle': shipment.vehicle,
                'driver': shipment.driver,
                'distance_km': distance_km,
                'estimated_fuel_liters': estimated_fuel_liters,
                'actual_fuel_liters': actual_fuel_liters,
                'fuel_efficiency_km_per_liter': calcs['fuel_efficiency'],
                'fuel_variance_liters': calcs['fuel_variance_liters'],
                'fuel_variance_percentage': calcs['fuel_variance_percentage'],
                'data_source': data_source,
                'notes': notes,
            }
        )

    return record


def generate_fuel_recommendations(*, vehicle_id=None, driver_id=None, analyzer=None) -> List[Dict[str, Any]]:
    """
    FR-07.2 Generates rule-based fuel optimization recommendations.
    """
    if analyzer is None:
        analyzer = RuleBasedFuelAnalyzer()

    recommendations = []
    if vehicle_id:
        recs = analyzer.analyze_vehicle_efficiency(str(vehicle_id))
        recommendations.extend(recs)
    if driver_id:
        recs = analyzer.analyze_driver_efficiency(str(driver_id))
        recommendations.extend(recs)

    results = []
    for r in recommendations:
        if r:
            results.append({
                "category": r.category,
                "title": r.title,
                "severity": r.severity,
                "message": r.message,
                "actionable_advice": r.actionable_advice,
                "metadata": r.metadata
            })
    return results
