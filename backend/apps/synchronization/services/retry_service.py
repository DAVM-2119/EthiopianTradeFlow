from django.utils import timezone
from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices
from apps.core.exceptions import NotFoundException, ConflictException, PermissionDeniedException

def retry_failed_sync_event(*, user, client_event_id):
    """
    Retries processing for a previously FAILED sync event.
    Re-executes sync event processing inside transaction.
    """
    sync_event = OfflineSyncEvent.objects.filter(client_event_id=client_event_id).first()
    if not sync_event:
        raise NotFoundException("Offline sync event not found.")

    if not (user.is_staff or getattr(user, 'role', '') == 'ADMIN') and sync_event.user != user:
        raise PermissionDeniedException("You are not authorized to retry this sync event.")

    if sync_event.status == SyncStatusChoices.SYNCED:
        return sync_event

    if sync_event.status == SyncStatusChoices.CONFLICT:
        raise ConflictException("Cannot retry an event marked as CONFLICT.")

    from apps.synchronization.services.sync_service import execute_sync_event_processing
    return execute_sync_event_processing(sync_event)
