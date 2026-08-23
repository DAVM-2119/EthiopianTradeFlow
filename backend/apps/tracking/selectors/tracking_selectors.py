from apps.tracking.models import TrackingEvent

def get_tracking_event_by_id(event_id):
    return TrackingEvent.objects.select_related('shipment', 'driver').filter(id=event_id).first()


def get_shipment_tracking_events(shipment_id, limit=100):
    return TrackingEvent.objects.select_related('shipment', 'driver').filter(
        shipment_id=shipment_id
    ).order_by('-recorded_at')[:limit]


def get_latest_tracking_event(shipment_id):
    return TrackingEvent.objects.select_related('shipment', 'driver').filter(
        shipment_id=shipment_id
    ).order_by('-recorded_at').first()


def get_driver_tracking_events(driver_user, limit=100):
    return TrackingEvent.objects.select_related('shipment', 'driver').filter(
        driver=driver_user
    ).order_by('-recorded_at')[:limit]
