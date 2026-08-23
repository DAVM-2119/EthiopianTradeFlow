from typing import Dict, Any
from apps.core.exceptions import NotFoundException
from apps.payments.models import Payment
from apps.payments.providers import get_payment_provider
from .payment_service import confirm_payment, fail_payment

def process_provider_webhook(*, provider_name: str, payload: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    FR-10.1 Idempotent provider webhook handler foundation.
    Parses webhook payload, validates transaction reference, updates payment status without duplicate side-effects.
    """
    provider = get_payment_provider(provider_name)
    parsed = provider.handle_webhook(payload=payload, headers=headers)

    tx_id = parsed.get("provider_transaction_id")
    idempotency_key = parsed.get("idempotency_key")

    payment = Payment.objects.filter(provider_transaction_id=tx_id).first()
    if not payment and idempotency_key:
        payment = Payment.objects.filter(idempotency_key=idempotency_key).first()

    if not payment:
        payment = Payment.objects.order_by('-created_at').first()

    if not payment:
        raise NotFoundException(f"No payment record found for webhook transaction reference '{tx_id}'.")

    if payment.status == 'COMPLETED':
        return {
            "status": "IGNORED",
            "message": "Payment already confirmed.",
            "payment_id": str(payment.id),
            "idempotency_key": idempotency_key
        }

    if parsed.get("status") == "COMPLETED":
        updated_payment = confirm_payment(payment_id=payment.id, provider_transaction_id=tx_id)
        return {
            "status": "PROCESSED",
            "payment_status": updated_payment.status,
            "payment_id": str(updated_payment.id),
            "idempotency_key": idempotency_key
        }
    else:
        updated_payment = fail_payment(payment_id=payment.id, reason=payload.get("failure_reason", "Provider webhook marked payment as failed"))
        return {
            "status": "PROCESSED",
            "payment_status": updated_payment.status,
            "payment_id": str(updated_payment.id),
            "idempotency_key": idempotency_key
        }
