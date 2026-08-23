from django.db import transaction
from apps.marketplace.models import Load, LoadStatusChoices
from apps.core.exceptions import ValidationException, ConflictException, PermissionDeniedException, NotFoundException

def create_load(shipper_user, validated_data):
    """
    Creates a new load for shipper_user.
    """
    status_choice = validated_data.pop('status', LoadStatusChoices.DRAFT)
    load = Load(shipper=shipper_user, status=status_choice, **validated_data)
    load.full_clean()
    load.save()
    return load


def update_load(load, user, validated_data):
    """
    Updates an existing load. Enforces ownership and validates fields.
    Blocks direct modifications to status through standard update.
    """
    if load.shipper != user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to update this load.")

    if load.status == LoadStatusChoices.CANCELLED:
        raise ConflictException("Cancelled loads cannot be modified.")

    validated_data.pop('status', None)

    for attr, value in validated_data.items():
        setattr(load, attr, value)

    load.full_clean()
    load.save()
    return load


def post_load(load, user):
    """
    Transitions load state from DRAFT -> POSTED atomically.
    """
    if load.shipper != user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to post this load.")

    if load.status == LoadStatusChoices.POSTED:
        raise ConflictException("Load is already posted.")

    if load.status == LoadStatusChoices.CANCELLED:
        raise ConflictException("Cancelled loads cannot be posted.")

    with transaction.atomic():
        load.status = LoadStatusChoices.POSTED
        load.save(update_fields=['status', 'updated_at'])

    return load


def cancel_load(load, user):
    """
    Transitions load state to CANCELLED atomically.
    """
    if load.shipper != user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to cancel this load.")

    if load.status == LoadStatusChoices.CANCELLED:
        raise ConflictException("Load is already cancelled.")

    with transaction.atomic():
        load.status = LoadStatusChoices.CANCELLED
        load.save(update_fields=['status', 'updated_at'])

    return load
