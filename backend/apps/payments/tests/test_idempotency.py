import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import Payment
from apps.payments.services import create_payment

@pytest.mark.django_db
def test_payment_creation_idempotency():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_idem@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_idem@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="Idempotency Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("40000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    p1 = create_payment(
        shipment_id=shipment.id, payer_id=shipper.id, amount=Decimal("40000.00"), idempotency_key="idemp-key-abc-123"
    )

    p2 = create_payment(
        shipment_id=shipment.id, payer_id=shipper.id, amount=Decimal("40000.00"), idempotency_key="idemp-key-abc-123"
    )

    assert p1.id == p2.id
    assert Payment.objects.filter(idempotency_key="idemp-key-abc-123").count() == 1
