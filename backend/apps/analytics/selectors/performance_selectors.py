from calendar import monthrange
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db.models import Avg, Q

from apps.analytics.models import TransporterPerformance

def get_period_dates(year: int, month: int):
    """
    Returns start and end datetimes for a given year and month.
    """
    start_dt = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
    _, last_day = monthrange(year, month)
    end_dt = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))
    return start_dt, end_dt


def get_transporter_performance(transporter_id, year: Optional[int] = None, month: Optional[int] = None) -> Optional[TransporterPerformance]:
    """
    Retrieves stored TransporterPerformance record for a transporter. Defaults to current month if year/month not provided.
    """
    now = timezone.now()
    y = year or now.year
    m = month or now.month
    return TransporterPerformance.objects.filter(transporter_id=transporter_id, year=y, month=m).first()


def get_transporter_performance_history(transporter_id, limit: int = 12) -> List[TransporterPerformance]:
    """
    Retrieves historical TransporterPerformance records for a transporter.
    """
    return list(TransporterPerformance.objects.filter(transporter_id=transporter_id).order_by('-year', '-month')[:limit])


def get_corridor_benchmark_data(year: int, month: int) -> Dict[str, Any]:
    """
    Calculates anonymized corridor-wide benchmark averages across all transporters for a period.
    """
    period_str = f"{year:04d}-{month:02d}"
    qs = TransporterPerformance.objects.filter(year=year, month=month, completed_trips__gt=0)
    
    total_transporters = qs.count()
    if total_transporters == 0:
        return {
            "period": period_str,
            "total_transporters_benchmarked": 0,
            "on_time_delivery_rate": 0.0,
            "incident_rate": 0.0,
            "fuel_efficiency": None,
            "average_rating": None
        }

    agg = qs.aggregate(
        avg_on_time=Avg('on_time_delivery_rate'),
        avg_incident=Avg('incident_rate'),
        avg_fuel=Avg('fuel_efficiency', filter=Q(fuel_efficiency__isnull=False)),
        avg_rating=Avg('average_rating', filter=Q(average_rating__isnull=False))
    )

    return {
        "period": period_str,
        "total_transporters_benchmarked": total_transporters,
        "on_time_delivery_rate": float(round(agg['avg_on_time'] or Decimal('0.00'), 2)),
        "incident_rate": float(round(agg['avg_incident'] or Decimal('0.00'), 2)),
        "fuel_efficiency": float(round(agg['avg_fuel'], 2)) if agg['avg_fuel'] is not None else None,
        "average_rating": float(round(agg['avg_rating'], 2)) if agg['avg_rating'] is not None else None
    }
