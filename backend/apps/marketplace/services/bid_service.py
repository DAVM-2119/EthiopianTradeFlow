from django.utils import timezone
from django.db import transaction
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.verification.services import is_marketplace_eligible
from apps.core.exceptions import ValidationException, ConflictException, PermissionDeniedException, NotFoundException

def create_bid(*, transporter_user, load_id, validated_data):
    """
    Creates a new bid for transporter_user on load_id.
    Validates transporter verification, role, load status, and non-self-bidding.
    """
    if getattr(transporter_user, 'role', '') not in ('TRANSPORTER', 'FREIGHT_FORWARDER'):
        raise PermissionDeniedException("Only transporters and freight forwarders can place bids.")

    if not is_marketplace_eligible(transporter_user):
        raise PermissionDeniedException("You must be a verified transporter with an eligible fleet vehicle to place a bid.")

    load = Load.objects.filter(id=load_id).first()
    if not load:
        raise NotFoundException("Load not found.")

    if load.status != LoadStatusChoices.POSTED:
        raise ConflictException("Bids can only be placed on POSTED loads.")

    if load.shipper == transporter_user:
        raise ValidationException("Transporters cannot bid on their own load.")

    existing_active = Bid.objects.filter(load=load, transporter=transporter_user, status=BidStatusChoices.ACTIVE).first()
    if existing_active:
        raise ConflictException("You already have an active bid for this load. Please update your existing bid.")

    bid = Bid(
        load=load,
        transporter=transporter_user,
        status=BidStatusChoices.ACTIVE,
        **validated_data
    )
    bid.full_clean()
    bid.save()
    return bid


def update_bid(*, bid, user, validated_data):
    """
    Updates an active bid. Enforces ownership and active status.
    """
    if bid.transporter != user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to update this bid.")

    if bid.status != BidStatusChoices.ACTIVE:
        raise ConflictException("Only ACTIVE bids can be updated.")

    if bid.load.status != LoadStatusChoices.POSTED:
        raise ConflictException("Bids cannot be updated once the load is no longer POSTED.")

    validated_data.pop('status', None)
    validated_data.pop('transporter', None)
    validated_data.pop('load', None)

    for attr, value in validated_data.items():
        setattr(bid, attr, value)

    bid.full_clean()
    bid.save()
    return bid


def withdraw_bid(*, bid, user):
    """
    Withdraws an active bid atomically.
    """
    if bid.transporter != user and not (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("You do not have permission to withdraw this bid.")

    if bid.status != BidStatusChoices.ACTIVE:
        raise ConflictException("Only ACTIVE bids can be withdrawn.")

    with transaction.atomic():
        now = timezone.now()
        bid.status = BidStatusChoices.WITHDRAWN
        bid.withdrawn_at = now
        bid.save(update_fields=['status', 'withdrawn_at', 'updated_at'])

    return bid


def accept_bid(*, bid_id, load_owner_user):
    """
    Accepts a bid and books the load atomically with select_for_update row locking.
    Transitions target bid -> ACCEPTED, load -> BOOKED, and competing active bids -> REJECTED.
    """
    with transaction.atomic():
        bid = Bid.objects.select_for_update().filter(id=bid_id).first()
        if not bid:
            raise NotFoundException("Bid not found.")

        load = Load.objects.select_for_update().filter(id=bid.load_id).first()
        if not load:
            raise NotFoundException("Associated load not found.")

        if load.shipper != load_owner_user and not (load_owner_user.is_staff or getattr(load_owner_user, 'role', '') == 'ADMIN'):
            raise PermissionDeniedException("Only the owner of the load can accept bids.")

        if load.status != LoadStatusChoices.POSTED:
            raise ConflictException("Load is no longer available for bidding.")

        if bid.status != BidStatusChoices.ACTIVE:
            raise ConflictException("Only ACTIVE bids can be accepted.")

        now = timezone.now()
        if bid.expires_at and bid.expires_at <= now:
            bid.status = BidStatusChoices.EXPIRED
            bid.save(update_fields=['status', 'updated_at'])
            raise ConflictException("This bid has expired and cannot be accepted.")

        bid.status = BidStatusChoices.ACCEPTED
        bid.accepted_at = now
        bid.save(update_fields=['status', 'accepted_at', 'updated_at'])

        load.status = LoadStatusChoices.BOOKED
        load.save(update_fields=['status', 'updated_at'])

        Bid.objects.filter(load=load, status=BidStatusChoices.ACTIVE).exclude(id=bid.id).update(status=BidStatusChoices.REJECTED)

    return bid
