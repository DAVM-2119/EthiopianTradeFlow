from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices

def get_sync_event_by_client_id(*, user, client_event_id):
    """
    Retrieves an OfflineSyncEvent by client_event_id for the given user (or admin).
    """
    qs = OfflineSyncEvent.objects.filter(client_event_id=client_event_id)
    if not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        qs = qs.filter(user=user)
    return qs.first()


def get_user_sync_events(*, user, status=None, event_type=None):
    """
    Retrieves list of offline sync events for user with optional status/type filters.
    """
    qs = OfflineSyncEvent.objects.filter(user=user)
    if status:
        qs = qs.filter(status=status)
    if event_type:
        qs = qs.filter(event_type=event_type)
    return qs.order_by('-client_created_at')


def get_sync_status_summary(*, user):
    """
    Returns counts of user's sync events by status.
    """
    events = OfflineSyncEvent.objects.filter(user=user)
    return {
        'total': events.count(),
        'pending': events.filter(status=SyncStatusChoices.PENDING).count(),
        'syncing': events.filter(status=SyncStatusChoices.SYNCING).count(),
        'synced': events.filter(status=SyncStatusChoices.SYNCED).count(),
        'failed': events.filter(status=SyncStatusChoices.FAILED).count(),
        'conflict': events.filter(status=SyncStatusChoices.CONFLICT).count(),
    }
