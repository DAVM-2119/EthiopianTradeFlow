import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def publish_tracking_event(tracking_event):
    """
    Publishes a formatted GPS tracking update to the shipment channel group via Redis channel layer.
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        group_name = f"shipment_{tracking_event.shipment_id}"
        payload = {
            "type": "tracking.position_updated",
            "shipment_id": str(tracking_event.shipment_id),
            "event_id": tracking_event.event_id or "",
            "latitude": float(tracking_event.latitude),
            "longitude": float(tracking_event.longitude),
            "speed": float(tracking_event.speed) if tracking_event.speed is not None else None,
            "heading": float(tracking_event.heading) if tracking_event.heading is not None else None,
            "recorded_at": tracking_event.recorded_at.isoformat(),
            "received_at": tracking_event.received_at.isoformat(),
        }

        async_to_sync(channel_layer.group_send)(group_name, payload)
    except Exception as e:
        logger.error(f"Failed to publish WebSocket tracking event for shipment {tracking_event.shipment_id}: {e}")
