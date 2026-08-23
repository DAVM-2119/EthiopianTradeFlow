from apps.tracking.models import TrackingEvent
from apps.shipments.models import ShipmentEvent

def check_sync_conflict(*, event_type, entity_id, client_created_at):
    """
    Evaluates conflict status based on timestamp comparison against authoritative server state.
    Returns (has_conflict: bool, error_code: str, error_message: str).
    """
    if not entity_id:
        return False, "", ""

    if event_type == 'TRACKING_EVENT':
        newer_event = TrackingEvent.objects.filter(
            shipment_id=entity_id,
            recorded_at__gt=client_created_at
        ).first()
        if newer_event:
            return True, "STALE_TIMESTAMP", f"Tracking event timestamp {client_created_at} is older than recorded server position at {newer_event.recorded_at}."

    elif event_type in ('WAYPOINT_CHECKIN', 'INCIDENT_REPORT'):
        newer_event = ShipmentEvent.objects.filter(
            shipment_id=entity_id,
            created_at__gt=client_created_at
        ).first()
        if newer_event:
            return True, "STALE_TIMESTAMP", f"Shipment event timestamp {client_created_at} is older than processed server event at {newer_event.created_at}."

    return False, "", ""
