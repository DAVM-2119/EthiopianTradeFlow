from django.utils import timezone
from django.db import transaction
from apps.shipments.models import Shipment, ShipmentStatusChoices, ShipmentEvent
from apps.core.exceptions import ConflictException, ValidationException

ALLOWED_TRANSITIONS = {
    ShipmentStatusChoices.BOOKED: {
        ShipmentStatusChoices.ASSIGNED,
        ShipmentStatusChoices.CANCELLED,
        ShipmentStatusChoices.FAILED,
    },
    ShipmentStatusChoices.ASSIGNED: {
        ShipmentStatusChoices.PICKUP_READY,
        ShipmentStatusChoices.CANCELLED,
        ShipmentStatusChoices.FAILED,
    },
    ShipmentStatusChoices.PICKUP_READY: {
        ShipmentStatusChoices.IN_TRANSIT,
        ShipmentStatusChoices.CANCELLED,
        ShipmentStatusChoices.FAILED,
    },
    ShipmentStatusChoices.IN_TRANSIT: {
        ShipmentStatusChoices.CUSTOMS_PROCESSING,
        ShipmentStatusChoices.DELIVERED,
        ShipmentStatusChoices.FAILED,
        ShipmentStatusChoices.DISPUTED,
    },
    ShipmentStatusChoices.CUSTOMS_PROCESSING: {
        ShipmentStatusChoices.CUSTOMS_CLEARED,
        ShipmentStatusChoices.IN_TRANSIT,
        ShipmentStatusChoices.FAILED,
        ShipmentStatusChoices.DISPUTED,
    },
    ShipmentStatusChoices.CUSTOMS_CLEARED: {
        ShipmentStatusChoices.IN_TRANSIT,
        ShipmentStatusChoices.DELIVERED,
        ShipmentStatusChoices.FAILED,
        ShipmentStatusChoices.DISPUTED,
    },
    ShipmentStatusChoices.DELIVERED: {
        ShipmentStatusChoices.COMPLETED,
        ShipmentStatusChoices.DISPUTED,
    },
    ShipmentStatusChoices.COMPLETED: set(),
    ShipmentStatusChoices.CANCELLED: set(),
    ShipmentStatusChoices.FAILED: set(),
    ShipmentStatusChoices.DISPUTED: set(),
}


def transition_shipment(*, shipment, target_status, actor, description=''):
    """
    Executes a controlled state transition on a shipment and records a ShipmentEvent audit log.
    """
    current_status = shipment.status
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    if target_status not in allowed:
        raise ConflictException(f"Invalid shipment status transition from '{current_status}' to '{target_status}'.")

    if target_status == ShipmentStatusChoices.COMPLETED:
        if not hasattr(shipment, 'proof_of_delivery') or not shipment.proof_of_delivery:
            raise ValidationException("Proof of delivery is required before completing a shipment.")

    with transaction.atomic():
        now = timezone.now()
        update_fields = ['status', 'updated_at']

        if target_status == ShipmentStatusChoices.ASSIGNED and not shipment.assigned_at:
            shipment.assigned_at = now
            update_fields.append('assigned_at')
        elif target_status == ShipmentStatusChoices.PICKUP_READY and not shipment.pickup_ready_at:
            shipment.pickup_ready_at = now
            update_fields.append('pickup_ready_at')
        elif target_status == ShipmentStatusChoices.IN_TRANSIT and not shipment.departed_at:
            shipment.departed_at = now
            update_fields.append('departed_at')
        elif target_status == ShipmentStatusChoices.CUSTOMS_PROCESSING and not shipment.customs_processing_at:
            shipment.customs_processing_at = now
            update_fields.append('customs_processing_at')
        elif target_status == ShipmentStatusChoices.CUSTOMS_CLEARED and not shipment.customs_cleared_at:
            shipment.customs_cleared_at = now
            update_fields.append('customs_cleared_at')
        elif target_status == ShipmentStatusChoices.DELIVERED and not shipment.delivered_at:
            shipment.delivered_at = now
            update_fields.append('delivered_at')
        elif target_status == ShipmentStatusChoices.COMPLETED and not shipment.completed_at:
            shipment.completed_at = now
            update_fields.append('completed_at')
        elif target_status == ShipmentStatusChoices.FAILED and not shipment.failed_at:
            shipment.failed_at = now
            update_fields.append('failed_at')

        previous_status = shipment.status
        shipment.status = target_status
        shipment.save(update_fields=update_fields)

        event_desc = description or f"Shipment status transitioned from {previous_status} to {target_status}"
        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type='STATUS_TRANSITION',
            previous_status=previous_status,
            new_status=target_status,
            description=event_desc,
            created_by=actor
        )

    return shipment
