from django.utils import timezone
from apps.shipments.models import Shipment, ShipmentEvent, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent
from apps.eta.models import ETAPrediction
from apps.eta.predictors import ETAContext, RuleBasedETAPredictor
from apps.core.exceptions import NotFoundException

def calculate_and_save_eta(*, shipment_id, predictor=None):
    """
    Calculates and persists a new ETA prediction for a shipment.
    Uses RuleBasedETAPredictor by default, allowing ML model injection in Phase 25.
    """
    shipment = Shipment.objects.select_related('load').filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    if shipment.status in (ShipmentStatusChoices.COMPLETED, ShipmentStatusChoices.CANCELLED, ShipmentStatusChoices.FAILED):
        return ETAPrediction.objects.filter(shipment_id=shipment_id).order_by('-predicted_at').first()

    if predictor is None:
        predictor = RuleBasedETAPredictor()

    # Fetch latest tracking event & recent speed history
    recent_events = list(TrackingEvent.objects.filter(shipment_id=shipment_id).order_by('-recorded_at')[:5])

    current_lat = None
    current_lon = None
    current_speed = None
    recent_avg_speed = None

    if recent_events:
        latest = recent_events[0]
        current_lat = float(latest.latitude)
        current_lon = float(latest.longitude)
        if latest.speed is not None:
            current_speed = float(latest.speed)

        speeds = [float(e.speed) for e in recent_events if e.speed is not None and float(e.speed) > 0]
        if speeds:
            recent_avg_speed = sum(speeds) / len(speeds)

    # Calculate known delay minutes from shipment incident reports
    incident_count = ShipmentEvent.objects.filter(
        shipment_id=shipment_id,
        event_type='INCIDENT_REPORT'
    ).count()
    known_delay_minutes = incident_count * 30  # Assume 30 mins delay per reported incident

    now = timezone.now()
    context = ETAContext(
        shipment_id=str(shipment.id),
        origin_city=shipment.load.origin_city,
        destination_city=shipment.load.destination_city,
        current_latitude=current_lat,
        current_longitude=current_lon,
        current_speed_kmh=current_speed,
        recent_average_speed_kmh=recent_avg_speed,
        known_delay_minutes=known_delay_minutes,
        timestamp=now
    )

    result = predictor.predict(context)

    prediction = ETAPrediction.objects.create(
        shipment=shipment,
        predicted_at=now,
        estimated_arrival=result.estimated_arrival,
        remaining_distance_km=result.remaining_distance_km,
        expected_speed_kmh=result.expected_speed_kmh,
        delay_minutes=result.delay_minutes,
        prediction_method=result.prediction_method,
        algorithm_version=result.algorithm_version,
        confidence=result.confidence
    )

    return prediction
