from decimal import Decimal
from django.contrib.gis.geos import Point
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.tracking.models import TrackingEvent
from apps.core.exceptions import ValidationException, ConflictException, PermissionDeniedException, NotFoundException

TRACKABLE_STATUSES = {
    ShipmentStatusChoices.ASSIGNED,
    ShipmentStatusChoices.PICKUP_READY,
    ShipmentStatusChoices.IN_TRANSIT,
    ShipmentStatusChoices.CUSTOMS_PROCESSING,
    ShipmentStatusChoices.CUSTOMS_CLEARED,
}

TERMINAL_STATUSES = {
    ShipmentStatusChoices.COMPLETED,
    ShipmentStatusChoices.CANCELLED,
    ShipmentStatusChoices.FAILED,
}

def record_tracking_event(*, shipment_id, driver_user, latitude, longitude, speed=None, heading=None, recorded_at, event_id=None):
    """
    Ingests and records a GPS tracking event for an operational shipment.
    Includes validation for coordinates, speed, heading, driver assignment, trackable state, and duplicate prevention.
    """
    shipment = Shipment.objects.select_related('driver', 'transporter').filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    is_assigned_driver = (shipment.driver == driver_user)
    is_assigned_transporter = (shipment.transporter == driver_user)
    is_admin = driver_user.is_staff or getattr(driver_user, 'role', '') == 'ADMIN'

    if not (is_assigned_driver or is_assigned_transporter or is_admin):
        raise PermissionDeniedException("You are not authorized to submit GPS tracking events for this shipment.")

    if shipment.status in TERMINAL_STATUSES:
        raise ConflictException(f"Cannot record tracking events for shipment in terminal status '{shipment.status}'.")

    if shipment.status not in TRACKABLE_STATUSES:
        raise ConflictException(f"Shipment is not currently in a trackable status (Current: '{shipment.status}').")

    lat = Decimal(str(latitude))
    lon = Decimal(str(longitude))
    if lat < Decimal('-90.000000') or lat > Decimal('90.000000'):
        raise ValidationException("Latitude must be between -90 and 90 degrees.")
    if lon < Decimal('-180.000000') or lon > Decimal('180.000000'):
        raise ValidationException("Longitude must be between -180 and 180 degrees.")

    if speed is not None:
        spd = Decimal(str(speed))
        if spd < Decimal('0.00'):
            raise ValidationException("Speed cannot be negative.")

    if heading is not None:
        hdg = Decimal(str(heading))
        if hdg < Decimal('0.00') or hdg >= Decimal('360.00'):
            raise ValidationException("Heading must be in range [0, 360).")

    if event_id:
        existing = TrackingEvent.objects.filter(event_id=event_id).first()
        if existing:
            return existing

    location_point = Point(float(lon), float(lat), srid=4326)

    tracking_event = TrackingEvent.objects.create(
        event_id=event_id,
        shipment=shipment,
        driver=driver_user,
        location=location_point,
        latitude=lat,
        longitude=lon,
        speed=speed,
        heading=heading,
        recorded_at=recorded_at
    )

    return tracking_event
