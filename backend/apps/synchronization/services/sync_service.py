from django.db import transaction
from django.utils import timezone
from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices, SyncEventTypeChoices
from apps.synchronization.services.conflict_service import check_sync_conflict
from apps.tracking.services import record_tracking_event
from apps.shipments.services import record_waypoint_checkin, record_incident_report
from apps.core.exceptions import ValidationException

def process_sync_event(*, user, data):
    """
    Main entry point for single offline event submission.
    Guarantees idempotency by returning pre-existing SYNCED records.
    Handles conflict resolution, transaction safety, and domain dispatching.
    """
    client_event_id = data.get('client_event_id')
    if not client_event_id:
        raise ValidationException("client_event_id is required.")

    existing = OfflineSyncEvent.objects.filter(client_event_id=client_event_id).first()
    if existing:
        if existing.status == SyncStatusChoices.SYNCED:
            return existing
        sync_event = existing
    else:
        sync_event = OfflineSyncEvent.objects.create(
            client_event_id=client_event_id,
            user=user,
            device_id=data.get('device_id', ''),
            event_type=data['event_type'],
            entity_type=data.get('entity_type', 'shipment'),
            entity_id=data.get('entity_id'),
            payload=data.get('payload', {}),
            client_created_at=data['client_created_at'],
            client_updated_at=data.get('client_updated_at'),
            status=SyncStatusChoices.PENDING
        )

    return execute_sync_event_processing(sync_event)


def execute_sync_event_processing(sync_event):
    """
    Executes domain processing inside transaction.atomic().
    """
    sync_event.status = SyncStatusChoices.SYNCING
    sync_event.attempt_count += 1
    sync_event.last_attempt_at = timezone.now()
    sync_event.save(update_fields=['status', 'attempt_count', 'last_attempt_at'])

    has_conflict, err_code, err_msg = check_sync_conflict(
        event_type=sync_event.event_type,
        entity_id=sync_event.entity_id,
        client_created_at=sync_event.client_created_at
    )
    if has_conflict:
        sync_event.status = SyncStatusChoices.CONFLICT
        sync_event.error_code = err_code
        sync_event.error_message = err_msg
        sync_event.save(update_fields=['status', 'error_code', 'error_message'])
        return sync_event

    try:
        with transaction.atomic():
            server_entity = dispatch_domain_event(sync_event)

            server_entity_id = ""
            if hasattr(server_entity, 'event_id') and server_entity.event_id:
                server_entity_id = str(server_entity.event_id)
            elif hasattr(server_entity, 'id'):
                server_entity_id = str(server_entity.id)

            sync_event.status = SyncStatusChoices.SYNCED
            sync_event.synced_at = timezone.now()
            sync_event.server_entity_id = server_entity_id
            sync_event.error_code = ""
            sync_event.error_message = ""
            sync_event.save(update_fields=['status', 'synced_at', 'server_entity_id', 'error_code', 'error_message'])

    except Exception as e:
        sync_event.status = SyncStatusChoices.FAILED
        sync_event.error_code = e.__class__.__name__
        sync_event.error_message = str(e)
        sync_event.save(update_fields=['status', 'error_code', 'error_message'])

    return sync_event


def dispatch_domain_event(sync_event):
    """
    Dispatches OfflineSyncEvent to underlying domain service.
    """
    p = sync_event.payload or {}
    user = sync_event.user
    entity_id = sync_event.entity_id

    if sync_event.event_type == SyncEventTypeChoices.TRACKING_EVENT:
        return record_tracking_event(
            shipment_id=entity_id,
            driver_user=user,
            latitude=p['latitude'],
            longitude=p['longitude'],
            speed=p.get('speed'),
            heading=p.get('heading'),
            recorded_at=p.get('recorded_at', sync_event.client_created_at),
            event_id=str(sync_event.client_event_id)
        )

    elif sync_event.event_type == SyncEventTypeChoices.WAYPOINT_CHECKIN:
        return record_waypoint_checkin(
            shipment_id=entity_id,
            user=user,
            latitude=p.get('latitude'),
            longitude=p.get('longitude'),
            recorded_at=p.get('recorded_at', sync_event.client_created_at),
            notes=p.get('notes', '')
        )

    elif sync_event.event_type == SyncEventTypeChoices.INCIDENT_REPORT:
        return record_incident_report(
            shipment_id=entity_id,
            user=user,
            incident_type=p.get('incident_type', 'GENERAL'),
            description=p.get('description', ''),
            recorded_at=p.get('recorded_at', sync_event.client_created_at),
            latitude=p.get('latitude'),
            longitude=p.get('longitude')
        )

    else:
        raise ValidationException(f"Unsupported event_type '{sync_event.event_type}'.")


def process_batch_sync_events(*, user, events_data):
    """
    Processes a list of offline sync events in batch.
    Returns array of per-event status dictionaries.
    """
    results = []
    for evt_data in events_data:
        try:
            sync_event = process_sync_event(user=user, data=evt_data)
            results.append({
                'client_event_id': str(sync_event.client_event_id),
                'status': sync_event.status,
                'server_entity_id': sync_event.server_entity_id,
                'synced_at': sync_event.synced_at.isoformat() if sync_event.synced_at else None,
                'error_code': sync_event.error_code,
                'error_message': sync_event.error_message,
            })
        except Exception as e:
            results.append({
                'client_event_id': str(evt_data.get('client_event_id', '')),
                'status': SyncStatusChoices.FAILED,
                'server_entity_id': '',
                'synced_at': None,
                'error_code': e.__class__.__name__,
                'error_message': str(e),
            })
    return results
