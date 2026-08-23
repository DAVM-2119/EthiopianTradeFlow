from django.db import models
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import User, RoleChoices
from apps.fleet.models import Vehicle, VehicleStatusChoices
from apps.profiles.models import TransporterProfile
from apps.shipments.models import Shipment, ShipmentStatusChoices, ShipmentEvent, ProofOfDelivery
from apps.shipments.services.shipment_transition_service import transition_shipment
from apps.core.exceptions import ValidationException, ConflictException, PermissionDeniedException, NotFoundException

def create_shipment_from_accepted_bid(*, load, bid, shipper, transporter):
    """
    Creates a new Shipment in BOOKED state from an accepted bid.
    Guarantees no duplicate shipments are created for the same bid or load.
    Must be called inside an active transaction.atomic() block.
    """
    existing = Shipment.objects.filter(models.Q(load=load) | models.Q(bid=bid)).first()
    if existing:
        return existing

    shipment = Shipment.objects.create(
        load=load,
        bid=bid,
        shipper=shipper,
        transporter=transporter,
        status=ShipmentStatusChoices.BOOKED
    )

    ShipmentEvent.objects.create(
        shipment=shipment,
        event_type='CREATED',
        previous_status='',
        new_status=ShipmentStatusChoices.BOOKED,
        description=f"Shipment created from accepted bid #{bid.id} for load {load.id}",
        created_by=shipper
    )
    return shipment


def assign_shipment_resources(*, shipment, actor, vehicle_id, driver_id):
    """
    Assigns operational vehicle and driver to a shipment.
    Validates transporter ownership, vehicle status, and driver role.
    Transitions status: BOOKED -> ASSIGNED.
    """
    if shipment.transporter != actor and not (actor.is_staff or getattr(actor, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("Only the assigned transporter or admin can assign shipment resources.")

    if shipment.status not in (ShipmentStatusChoices.BOOKED, ShipmentStatusChoices.ASSIGNED):
        raise ConflictException("Resources can only be assigned to BOOKED or ASSIGNED shipments.")

    prof = TransporterProfile.objects.filter(user=shipment.transporter).first()
    if not prof:
        raise ValidationException("Transporter profile not found.")

    vehicle = Vehicle.objects.filter(id=vehicle_id, transporter=prof).first()
    if not vehicle:
        raise NotFoundException("Vehicle not found or does not belong to transporter fleet.")

    if vehicle.status == VehicleStatusChoices.INACTIVE:
        raise ValidationException("Inactive vehicles cannot be assigned to a shipment.")

    driver = User.objects.filter(id=driver_id, is_active=True).first()
    if not driver:
        raise NotFoundException("Driver user not found.")

    if getattr(driver, 'role', '') != RoleChoices.DRIVER:
        raise ValidationException("User must have DRIVER role to be assigned to a shipment.")

    with transaction.atomic():
        now = timezone.now()
        shipment.vehicle = vehicle
        shipment.driver = driver
        shipment.assigned_at = now
        
        if shipment.status == ShipmentStatusChoices.BOOKED:
            previous_status = shipment.status
            shipment.status = ShipmentStatusChoices.ASSIGNED
            shipment.save(update_fields=['vehicle', 'driver', 'status', 'assigned_at', 'updated_at'])
            
            ShipmentEvent.objects.create(
                shipment=shipment,
                event_type='RESOURCE_ASSIGNMENT',
                previous_status=previous_status,
                new_status=ShipmentStatusChoices.ASSIGNED,
                description=f"Assigned vehicle {vehicle.registration_number} and driver {driver.email}",
                created_by=actor
            )
        else:
            shipment.save(update_fields=['vehicle', 'driver', 'updated_at'])
            ShipmentEvent.objects.create(
                shipment=shipment,
                event_type='RESOURCE_ASSIGNMENT_UPDATE',
                previous_status=shipment.status,
                new_status=shipment.status,
                description=f"Updated assigned vehicle to {vehicle.registration_number} and driver to {driver.email}",
                created_by=actor
            )

    return shipment


def cancel_shipment(*, shipment, actor, reason):
    """
    Cancels a shipment if in an allowed pre-delivery state (BOOKED, ASSIGNED, PICKUP_READY).
    """
    if shipment.shipper != actor and shipment.transporter != actor and not (actor.is_staff or getattr(actor, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to cancel this shipment.")

    if shipment.status not in (ShipmentStatusChoices.BOOKED, ShipmentStatusChoices.ASSIGNED, ShipmentStatusChoices.PICKUP_READY):
        raise ConflictException(f"Shipment cannot be cancelled from state '{shipment.status}'.")

    with transaction.atomic():
        now = timezone.now()
        previous_status = shipment.status
        shipment.status = ShipmentStatusChoices.CANCELLED
        shipment.cancelled_at = now
        shipment.cancelled_by = actor
        shipment.cancellation_reason = reason
        shipment.save(update_fields=['status', 'cancelled_at', 'cancelled_by', 'cancellation_reason', 'updated_at'])

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type='CANCELLED',
            previous_status=previous_status,
            new_status=ShipmentStatusChoices.CANCELLED,
            description=f"Shipment cancelled by {actor.email}. Reason: {reason}",
            created_by=actor
        )

    return shipment


def record_proof_of_delivery(*, shipment, actor, receiver_name, delivery_timestamp, signature_reference='', photo_reference='', notes=''):
    """
    Records Proof of Delivery for a DELIVERED shipment.
    """
    if shipment.transporter != actor and shipment.driver != actor and not (actor.is_staff or getattr(actor, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("Only the transporter, assigned driver, or admin can record proof of delivery.")

    if shipment.status != ShipmentStatusChoices.DELIVERED:
        raise ConflictException("Proof of delivery can only be recorded when shipment is DELIVERED.")

    if hasattr(shipment, 'proof_of_delivery') and shipment.proof_of_delivery:
        raise ConflictException("Proof of delivery has already been recorded for this shipment.")

    with transaction.atomic():
        pod = ProofOfDelivery.objects.create(
            shipment=shipment,
            receiver_name=receiver_name,
            delivery_timestamp=delivery_timestamp,
            signature_reference=signature_reference,
            photo_reference=photo_reference,
            notes=notes,
            submitted_by=actor
        )

        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type='POD_SUBMITTED',
            previous_status=shipment.status,
            new_status=shipment.status,
            description=f"Proof of delivery submitted by {actor.email}. Received by {receiver_name}.",
            created_by=actor
        )

    return pod


def complete_shipment(*, shipment, actor):
    """
    Completes a DELIVERED shipment after verifying Proof of Delivery exists.
    """
    if shipment.shipper != actor and shipment.transporter != actor and not (actor.is_staff or getattr(actor, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("Only the shipper, transporter, or admin can complete a shipment.")

    return transition_shipment(
        shipment=shipment,
        target_status=ShipmentStatusChoices.COMPLETED,
        actor=actor,
        description="Shipment completed upon verified proof of delivery."
    )
