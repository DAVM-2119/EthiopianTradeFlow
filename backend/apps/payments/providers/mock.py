import uuid
from typing import Dict, Any
from .base import BasePaymentProvider

class MockPaymentProvider(BasePaymentProvider):
    """
    Mock payment provider for development and testing.
    Simulates external mobile-money payment gateway interactions.
    """

    def initiate_payment(self, *, payment, **kwargs) -> Dict[str, Any]:
        tx_id = f"MOCK-TX-{uuid.uuid4().hex[:12].upper()}"
        return {
            "success": True,
            "provider": "MOCK",
            "provider_transaction_id": tx_id,
            "status": "INITIATED",
            "message": "Mock payment initiated successfully.",
            "checkout_url": f"https://checkout.mockpay.et/pay/{tx_id}"
        }

    def verify_payment(self, *, payment, provider_transaction_id: str, **kwargs) -> Dict[str, Any]:
        return {
            "success": True,
            "provider": "MOCK",
            "provider_transaction_id": provider_transaction_id or f"MOCK-TX-{uuid.uuid4().hex[:12].upper()}",
            "status": "COMPLETED",
            "amount": float(payment.amount),
            "currency": payment.currency
        }

    def handle_webhook(self, *, payload: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("event_type", "payment.success")
        tx_id = payload.get("transaction_id", f"MOCK-TX-{uuid.uuid4().hex[:12].upper()}")
        idempotency_key = payload.get("idempotency_key") or headers.get("HTTP_IDEMPOTENCY_KEY") or f"wh-idemp-{tx_id}"

        return {
            "event_type": event_type,
            "provider_transaction_id": tx_id,
            "idempotency_key": idempotency_key,
            "status": "COMPLETED" if event_type == "payment.success" else "FAILED",
            "payload": payload
        }

    def initiate_payout(self, *, payout, **kwargs) -> Dict[str, Any]:
        payout_tx_id = f"MOCK-PO-{uuid.uuid4().hex[:12].upper()}"
        return {
            "success": True,
            "provider": "MOCK",
            "provider_transaction_id": payout_tx_id,
            "status": "COMPLETED",
            "amount": float(payout.net_amount)
        }
