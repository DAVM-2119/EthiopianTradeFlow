import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import (
    Payment, PaymentStatusChoices, Commission, Payout, PayoutStatusChoices,
    Settlement, SettlementStatusChoices, PaymentDispute, DisputeStatusChoices
)
from apps.core.exceptions import ValidationException

@pytest.mark.django_db
def test_payment_models_and_state_machine():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_pay_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_pay_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="Payment Test Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("100000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    payment = Payment.objects.create(
        shipment=shipment,
        payer=shipper,
        amount=Decimal("100000.00"),
        currency="ETB",
        status=PaymentStatusChoices.PENDING,
        idempotency_key="key-test-m1"
    )

    assert payment.amount == Decimal("100000.00")
    assert payment.status == PaymentStatusChoices.PENDING

    payment.transition_to(PaymentStatusChoices.INITIATED)
    assert payment.status == PaymentStatusChoices.INITIATED

    with pytest.raises(ValidationException):
        payment.transition_to(PaymentStatusChoices.PENDING)
