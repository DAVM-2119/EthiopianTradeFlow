from decimal import Decimal
from typing import Dict, Any, Optional
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from apps.analytics.models import TripFuelRecord

def get_fuel_record_for_shipment(shipment_id):
    """
    Retrieves trip fuel record for a shipment.
    """
    return TripFuelRecord.objects.filter(shipment_id=shipment_id).select_related('shipment', 'vehicle', 'driver').first()


def get_fuel_records_for_vehicle(vehicle_id, start_date=None, end_date=None):
    """
    Retrieves fuel records for a vehicle with optional date filtering.
    """
    qs = TripFuelRecord.objects.filter(vehicle_id=vehicle_id).select_related('shipment', 'driver')
    if start_date:
        qs = qs.filter(recorded_at__gte=start_date)
    if end_date:
        qs = qs.filter(recorded_at__lte=end_date)
    return qs.order_by('-recorded_at')


def get_fuel_records_for_driver(driver_id, start_date=None, end_date=None):
    """
    Retrieves fuel records for a driver with optional date filtering.
    """
    qs = TripFuelRecord.objects.filter(driver_id=driver_id).select_related('shipment', 'vehicle')
    if start_date:
        qs = qs.filter(recorded_at__gte=start_date)
    if end_date:
        qs = qs.filter(recorded_at__lte=end_date)
    return qs.order_by('-recorded_at')


def get_vehicle_fuel_summary(vehicle_id, start_date=None, end_date=None) -> Dict[str, Any]:
    """
    Calculates vehicle-level fuel consumption analytics via SQL aggregations (FR-07.1).
    """
    qs = get_fuel_records_for_vehicle(vehicle_id, start_date, end_date)
    total_trips = qs.count()
    if total_trips == 0:
        return {
            "vehicle_id": str(vehicle_id),
            "total_trips": 0,
            "total_distance_km": 0.0,
            "total_estimated_fuel_liters": 0.0,
            "total_actual_fuel_liters": 0.0,
            "average_fuel_efficiency_km_per_liter": 0.0,
            "average_variance_percentage": 0.0
        }

    agg = qs.aggregate(
        tot_dist=Sum('distance_km'),
        tot_est=Sum('estimated_fuel_liters'),
        tot_act=Sum('actual_fuel_liters', filter=Q(actual_fuel_liters__gt=0)),
        avg_eff=Avg('fuel_efficiency_km_per_liter', filter=Q(fuel_efficiency_km_per_liter__gt=0)),
        avg_var=Avg('fuel_variance_percentage', filter=Q(fuel_variance_percentage__isnull=False))
    )

    tot_dist = float(agg['tot_dist'] or 0.0)
    tot_est = float(agg['tot_est'] or 0.0)
    tot_act = float(agg['tot_act'] or 0.0)
    avg_eff = float(agg['avg_eff'] or (tot_dist / tot_act if tot_act > 0 else (tot_dist / tot_est if tot_est > 0 else 0.0)))
    avg_var = float(agg['avg_var'] or 0.0)

    return {
        "vehicle_id": str(vehicle_id),
        "total_trips": total_trips,
        "total_distance_km": round(tot_dist, 2),
        "total_estimated_fuel_liters": round(tot_est, 2),
        "total_actual_fuel_liters": round(tot_act, 2),
        "average_fuel_efficiency_km_per_liter": round(avg_eff, 2),
        "average_variance_percentage": round(avg_var, 2)
    }


def get_driver_fuel_summary(driver_id, start_date=None, end_date=None) -> Dict[str, Any]:
    """
    Calculates driver-level fuel consumption analytics via SQL aggregations (FR-07.1).
    """
    qs = get_fuel_records_for_driver(driver_id, start_date, end_date)
    total_trips = qs.count()
    if total_trips == 0:
        return {
            "driver_id": str(driver_id),
            "total_trips": 0,
            "total_distance_km": 0.0,
            "total_estimated_fuel_liters": 0.0,
            "total_actual_fuel_liters": 0.0,
            "average_fuel_efficiency_km_per_liter": 0.0,
            "average_variance_percentage": 0.0
        }

    agg = qs.aggregate(
        tot_dist=Sum('distance_km'),
        tot_est=Sum('estimated_fuel_liters'),
        tot_act=Sum('actual_fuel_liters', filter=Q(actual_fuel_liters__gt=0)),
        avg_eff=Avg('fuel_efficiency_km_per_liter', filter=Q(fuel_efficiency_km_per_liter__gt=0)),
        avg_var=Avg('fuel_variance_percentage', filter=Q(fuel_variance_percentage__isnull=False))
    )

    tot_dist = float(agg['tot_dist'] or 0.0)
    tot_est = float(agg['tot_est'] or 0.0)
    tot_act = float(agg['tot_act'] or 0.0)
    avg_eff = float(agg['avg_eff'] or (tot_dist / tot_act if tot_act > 0 else (tot_dist / tot_est if tot_est > 0 else 0.0)))
    avg_var = float(agg['avg_var'] or 0.0)

    return {
        "driver_id": str(driver_id),
        "total_trips": total_trips,
        "total_distance_km": round(tot_dist, 2),
        "total_estimated_fuel_liters": round(tot_est, 2),
        "total_actual_fuel_liters": round(tot_act, 2),
        "average_fuel_efficiency_km_per_liter": round(avg_eff, 2),
        "average_variance_percentage": round(avg_var, 2)
    }


def get_fuel_trends_data(vehicle_id=None, driver_id=None, period='monthly'):
    """
    Groups historical fuel records by month or week for frontend charts.
    """
    qs = TripFuelRecord.objects.all()
    if vehicle_id:
        qs = qs.filter(vehicle_id=vehicle_id)
    if driver_id:
        qs = qs.filter(driver_id=driver_id)

    trunc_func = TruncWeek('recorded_at') if period == 'weekly' else TruncMonth('recorded_at')

    trends = qs.annotate(period_bucket=trunc_func).values('period_bucket').annotate(
        trip_count=Count('id'),
        total_distance=Sum('distance_km'),
        total_estimated_fuel=Sum('estimated_fuel_liters'),
        total_actual_fuel=Sum('actual_fuel_liters', filter=Q(actual_fuel_liters__gt=0)),
        avg_efficiency=Avg('fuel_efficiency_km_per_liter', filter=Q(fuel_efficiency_km_per_liter__gt=0)),
        avg_variance=Avg('fuel_variance_percentage', filter=Q(fuel_variance_percentage__isnull=False))
    ).order_by('period_bucket')

    results = []
    for t in trends:
        bucket_date = t['period_bucket'].strftime('%Y-%m-%d') if t['period_bucket'] else 'Unknown'
        results.append({
            "period": bucket_date,
            "trip_count": t['trip_count'],
            "total_distance_km": float(round(t['total_distance'] or Decimal('0.00'), 2)),
            "total_estimated_fuel_liters": float(round(t['total_estimated_fuel'] or Decimal('0.00'), 2)),
            "total_actual_fuel_liters": float(round(t['total_actual_fuel'] or Decimal('0.00'), 2)),
            "average_efficiency_km_per_liter": float(round(t['avg_efficiency'] or Decimal('0.00'), 2)),
            "average_variance_percentage": float(round(t['avg_variance'] or Decimal('0.00'), 2))
        })

    return results
