import pytest
from decimal import Decimal
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import PaymentStatusChoices, PayoutStatusChoices, SettlementStatusChoices
from apps.payments.services import create_payment, initiate_payment, confirm_payment, process_payout, raise_dispute, resolve_dispute

@pytest.mark.django_db
def test_payment_services_full_pipeline():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_pay_s@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_pay_s@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    admin = User.objects.create_user(email='admin_pay_s@tradeflow.et', password='Password123!', role=RoleChoices.ADMIN)

    load = Load.objects.create(
        shipper=shipper, title="Pipeline Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("100000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    payment = create_payment(
        shipment_id=shipment.id,
        payer_id=shipper.id,
        amount=Decimal("100000.00"),
        idempotency_key="idemp-svc-100"
    )
    assert payment.status == PaymentStatusChoices.PENDING

    initiated_payment = initiate_payment(payment_id=payment.id)
    assert initiated_payment.status == PaymentStatusChoices.INITIATED
    assert initiated_payment.provider_transaction_id is not None

    confirmed_payment = confirm_payment(payment_id=payment.id)
    assert confirmed_payment.status == PaymentStatusChoices.COMPLETED
    assert hasattr(confirmed_payment, 'commission')
    assert confirmed_payment.commission.commission_amount == Decimal("5000.00")
    assert confirmed_payment.commission.net_amount == Decimal("95000.00")

    payout = confirmed_payment.payouts.first()
    assert payout is not None
    assert payout.net_amount == Decimal("95000.00")

    settlement = confirmed_payment.settlements.first()
    assert settlement is not None
    assert settlement.status == SettlementStatusChoices.RECONCILED

    completed_payout = process_payout(payout_id=payout.id)
    assert completed_payout.status == PayoutStatusChoices.COMPLETED

    dispute = raise_dispute(
        payment_id=payment.id,
        raised_by_id=shipper.id,
        reason="AMOUNT_MISMATCH",
        description="Amount verified by bank differs"
    )
    assert dispute.status == "OPEN"

    resolved_dispute = resolve_dispute(
        dispute_id=dispute.id,
        resolved_by_id=admin.id,
        resolution_status="RESOLVED",
        resolution_notes="Audited and matched."
    )
    assert resolved_dispute.status == "RESOLVED"
