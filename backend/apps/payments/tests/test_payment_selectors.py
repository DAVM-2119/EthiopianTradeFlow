import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import Payment, PaymentStatusChoices
from apps.payments.selectors import (
    get_payment_by_id, get_payment_by_idempotency_key, get_payments_for_user,
    get_payouts_for_transporter, get_settlements_for_user, get_disputes_for_user
)

@pytest.mark.django_db
def test_payment_selectors():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_pay_sel@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_pay_sel@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="Selector Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("50000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    payment = Payment.objects.create(
        shipment=shipment, payer=shipper, amount=Decimal("50000.00"), currency="ETB", status=PaymentStatusChoices.PENDING, idempotency_key="idemp-sel-1"
    )

    p_by_id = get_payment_by_id(payment.id)
    assert p_by_id == payment

    p_by_key = get_payment_by_idempotency_key("idemp-sel-1")
    assert p_by_key == payment

    p_shipper_list = get_payments_for_user(shipper)
    assert len(p_shipper_list) == 1
