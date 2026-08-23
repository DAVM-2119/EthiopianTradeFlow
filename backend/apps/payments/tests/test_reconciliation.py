import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import Commission, Payout, Settlement
from apps.payments.services import create_payment, confirm_payment

@pytest.mark.django_db
def test_financial_reconciliation_pipeline():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_rec@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_rec@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="Reconciliation Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("20.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("200000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    payment = create_payment(
        shipment_id=shipment.id, payer_id=shipper.id, amount=Decimal("200000.00"), idempotency_key="idemp-rec-200"
    )

    confirm_payment(payment_id=payment.id)

    comm = Commission.objects.get(payment=payment)
    assert comm.gross_amount == Decimal("200000.00")
    assert comm.commission_amount == Decimal("10000.00")
    assert comm.net_amount == Decimal("190000.00")

    payout = Payout.objects.get(payment=payment)
    assert payout.transporter == transporter
    assert payout.net_amount == Decimal("190000.00")

    settlement = Settlement.objects.get(shipment=shipment)
    assert settlement.gross_amount == Decimal("200000.00")
    assert settlement.commission_amount == Decimal("10000.00")
    assert settlement.net_transporter_amount == Decimal("190000.00")
