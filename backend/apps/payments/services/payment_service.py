import uuid
from decimal import Decimal
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import NotFoundException, ValidationException
from apps.accounts.models import User
from apps.shipments.models import Shipment
from apps.payments.models import (
    Payment, PaymentStatusChoices, PaymentMethodChoices, PaymentProviderChoices,
    PaymentTransaction, PaymentTransactionStatusChoices
)
from apps.payments.providers import get_payment_provider
from .commission_service import calculate_commission
from .payout_service import create_payout
from .settlement_service import create_settlement

def create_payment(
    *,
    shipment_id: str,
    payer_id: str,
    amount: Decimal,
    idempotency_key: str,
    currency: str = 'ETB',
    payment_method: str = PaymentMethodChoices.MOBILE_MONEY,
    provider_name: str = PaymentProviderChoices.MOCK
) -> Payment:
    """
    FR-10.1 Creates customer payment record with strict idempotency.
    If idempotency_key already exists, returns existing payment record.
    """
    existing = Payment.objects.filter(idempotency_key=idempotency_key).select_related('shipment', 'payer').first()
    if existing:
        return existing

    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    payer = User.objects.filter(id=payer_id).first()
    if not payer:
        raise NotFoundException("Payer user not found.")

    if amount <= Decimal('0.00'):
        raise ValidationException("Payment amount must be greater than zero.")

    with transaction.atomic():
        payment = Payment.objects.create(
            shipment=shipment,
            payer=payer,
            amount=amount,
            currency=currency,
            status=PaymentStatusChoices.PENDING,
            payment_method=payment_method,
            provider=provider_name,
            idempotency_key=idempotency_key
        )

    return payment


def initiate_payment(*, payment_id: str) -> Payment:
    """
    FR-10.1 Initiates payment with the selected provider gateway.
    """
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        raise NotFoundException("Payment not found.")

    if payment.status in [PaymentStatusChoices.COMPLETED, PaymentStatusChoices.CANCELLED]:
        raise ValidationException(f"Cannot initiate payment in '{payment.status}' state.")

    provider = get_payment_provider(payment.provider)
    res = provider.initiate_payment(payment=payment)

    with transaction.atomic():
        payment.transition_to(PaymentStatusChoices.INITIATED, save=False)
        payment.initiated_at = timezone.now()
        payment.provider_transaction_id = res.get('provider_transaction_id')
        payment.save()

        PaymentTransaction.objects.create(
            payment=payment,
            provider=payment.provider,
            transaction_id=res.get('provider_transaction_id', f"TX-{uuid.uuid4().hex[:8]}"),
            status=PaymentTransactionStatusChoices.PENDING,
            raw_response=res
        )

    return payment


def confirm_payment(*, payment_id: str, provider_transaction_id: Optional[str] = None) -> Payment:
    """
    FR-10.1 & FR-10.2 Confirms payment, records transaction success, and atomically triggers financial reconciliation pipeline:
    Commission Calculation -> Settlement Record -> Transporter Payout.
    """
    payment = Payment.objects.filter(id=payment_id).select_related('shipment', 'payer').first()
    if not payment:
        raise NotFoundException("Payment not found.")

    if payment.status == PaymentStatusChoices.COMPLETED:
        return payment

    tx_id = provider_transaction_id or payment.provider_transaction_id or f"MOCK-CONF-{uuid.uuid4().hex[:8]}"

    with transaction.atomic():
        payment.transition_to(PaymentStatusChoices.COMPLETED, save=False)
        payment.confirmed_at = timezone.now()
        payment.provider_transaction_id = tx_id
        payment.save()

        PaymentTransaction.objects.create(
            payment=payment,
            provider=payment.provider,
            transaction_id=tx_id,
            status=PaymentTransactionStatusChoices.SUCCESS,
            raw_response={"status": "CONFIRMED", "confirmed_at": payment.confirmed_at.isoformat()}
        )

        comm = calculate_commission(payment=payment)
        payout = create_payout(payment=payment, commission=comm)
        create_settlement(payment=payment, commission=comm, payout=payout)

    return payment


def fail_payment(*, payment_id: str, reason: str = "Payment failed by provider") -> Payment:
    """
    Marks payment as FAILED.
    """
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        raise NotFoundException("Payment not found.")

    with transaction.atomic():
        payment.transition_to(PaymentStatusChoices.FAILED, save=False)
        payment.failed_at = timezone.now()
        payment.failure_reason = reason
        payment.save()

        PaymentTransaction.objects.create(
            payment=payment,
            provider=payment.provider,
            transaction_id=payment.provider_transaction_id or f"FAIL-{uuid.uuid4().hex[:8]}",
            status=PaymentTransactionStatusChoices.FAILED,
            raw_response={"reason": reason}
        )

    return payment
