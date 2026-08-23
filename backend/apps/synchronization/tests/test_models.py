import pytest
import uuid
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.synchronization.models import OfflineSyncEvent, SyncStatusChoices, SyncEventTypeChoices

@pytest.mark.django_db
def test_create_offline_sync_event():
    user = User.objects.create_user(email='driver_model@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    client_id = uuid.uuid4()
    now = timezone.now()

    event = OfflineSyncEvent.objects.create(
        client_event_id=client_id,
        user=user,
        device_id="device-001",
        event_type=SyncEventTypeChoices.WAYPOINT_CHECKIN,
        entity_type="shipment",
        entity_id=uuid.uuid4(),
        payload={"notes": "Checkin at Modjo"},
        client_created_at=now
    )

    assert event.client_event_id == client_id
    assert event.status == SyncStatusChoices.PENDING
    assert event.attempt_count == 0
    assert "SyncEvent" in str(event)
