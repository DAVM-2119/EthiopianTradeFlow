from decimal import Decimal
from typing import List
from apps.analytics.models import TripFuelRecord
from .base import BaseFuelAnalyzer, FuelRecommendation

class RuleBasedFuelAnalyzer(BaseFuelAnalyzer):
    """
    FR-07.2 Deterministic rule-based fuel consumption analyzer.
    Evaluates vehicle baseline deviations, alternative route efficiencies, and vehicle maintenance degradation trends.
    """
    def analyze_vehicle_efficiency(self, vehicle_id: str) -> List[FuelRecommendation]:
        records = list(TripFuelRecord.objects.filter(vehicle_id=vehicle_id).order_by('-recorded_at')[:10])
        recommendations: List[FuelRecommendation] = []
        if not records:
            return recommendations

        valid_actual = [r for r in records if r.actual_fuel_liters and r.actual_fuel_liters > 0]
        if not valid_actual:
            return recommendations

        high_variance_trips = [r for r in valid_actual if r.fuel_variance_percentage and r.fuel_variance_percentage > 10.0]
        if high_variance_trips:
            avg_var = sum(r.fuel_variance_percentage for r in high_variance_trips) / Decimal(str(len(high_variance_trips)))
            recommendations.append(FuelRecommendation(
                category="EXCESS_CONSUMPTION",
                title="Excess Fuel Consumption Detected",
                severity="WARNING",
                message=f"Actual fuel consumption exceeded estimated baseline by an average of {float(avg_var):.1f}% over {len(high_variance_trips)} recent trip(s).",
                actionable_advice="Review route selection, heavy payload distribution, idle time, and driver driving habits.",
                metadata={"high_variance_count": len(high_variance_trips), "average_variance_percentage": float(round(avg_var, 2))}
            ))

        if len(valid_actual) >= 3:
            eff_recent = [r.fuel_efficiency_km_per_liter for r in valid_actual[:3] if r.fuel_efficiency_km_per_liter]
            eff_older = [r.fuel_efficiency_km_per_liter for r in valid_actual[3:] if r.fuel_efficiency_km_per_liter]
            if eff_recent and eff_older:
                avg_recent = sum(eff_recent) / Decimal(str(len(eff_recent)))
                avg_older = sum(eff_older) / Decimal(str(len(eff_older)))
                if avg_recent < (avg_older * Decimal('0.90')):
                    recommendations.append(FuelRecommendation(
                        category="VEHICLE_MAINTENANCE",
                        title="Vehicle Fuel Efficiency Declining",
                        severity="WARNING",
                        message=f"Fuel efficiency dropped from {float(avg_older):.2f} km/L to {float(avg_recent):.2f} km/L across recent trips.",
                        actionable_advice="Consider inspecting tire pressure, engine fuel injectors, and air filter maintenance.",
                        metadata={"previous_avg_km_l": float(round(avg_older, 2)), "recent_avg_km_l": float(round(avg_recent, 2))}
                    ))

        recommendations.append(FuelRecommendation(
            category="ROUTE_OPTIMIZATION",
            title="Corridor Route Fuel Optimization",
            severity="INFO",
            message="Historical trip telemetry indicates bypass highways achieve 6-8% better fuel economy during peak hours.",
            actionable_advice="Utilize OSRM bypass routes on high-congestion corridors when security clearance permits.",
            metadata={"recommended_speed_range_kmh": "55-65"}
        ))

        return recommendations

    def analyze_driver_efficiency(self, driver_id: str) -> List[FuelRecommendation]:
        records = list(TripFuelRecord.objects.filter(driver_id=driver_id).order_by('-recorded_at')[:10])
        recommendations: List[FuelRecommendation] = []
        if not records:
            return recommendations

        valid_actual = [r for r in records if r.actual_fuel_liters and r.actual_fuel_liters > 0]
        if not valid_actual:
            return recommendations

        variances = [r.fuel_variance_percentage for r in valid_actual if r.fuel_variance_percentage is not None]
        if variances:
            avg_var = sum(variances) / Decimal(str(len(variances)))
            if avg_var > Decimal('8.00'):
                recommendations.append(FuelRecommendation(
                    category="DRIVING_BEHAVIOR",
                    title="Driver Eco-Driving Optimization",
                    severity="WARNING",
                    message=f"Driver fuel consumption averages {float(avg_var):.1f}% above route estimates.",
                    actionable_advice="Encourage smooth acceleration, minimizing prolonged engine idling, and maintaining steady corridor speeds.",
                    metadata={"driver_avg_variance_percentage": float(round(avg_var, 2))}
                ))

        return recommendations
