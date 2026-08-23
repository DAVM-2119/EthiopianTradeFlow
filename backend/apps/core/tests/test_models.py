import pytest
import uuid
from apps.core.models import BaseModel, AuditLog, ActionChoices

@pytest.mark.django_db
def test_base_model_uuid_and_timestamps():
    # Verify BaseModel is abstract
    assert BaseModel._meta.abstract is True

    log = AuditLog.objects.create(
        actor_id="user-123",
        action=ActionChoices.CREATE,
        resource_type="TestResource",
        resource_id="res-456",
        metadata={"detail": "sample"}
    )
    assert isinstance(log.id, uuid.UUID)
    assert log.created_at is not None
    assert log.updated_at is not None

    old_updated = log.updated_at
    log.action = ActionChoices.UPDATE
    log.save()
    log.refresh_from_db()
    assert log.updated_at >= old_updated


@pytest.mark.django_db
def test_audit_log_fields():
    log = AuditLog.objects.create(
        actor_id="admin-1",
        action=ActionChoices.VERIFY,
        resource_type="Transporter",
        resource_id="tr-789",
        metadata={"verified_by": "admin-1"}
    )
    assert log.actor_id == "admin-1"
    assert log.action == "VERIFY"
    assert log.resource_type == "Transporter"
    assert log.resource_id == "tr-789"
    assert log.metadata == {"verified_by": "admin-1"}
    assert "VERIFY" in str(log)
