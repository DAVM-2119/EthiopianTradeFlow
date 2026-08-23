from typing import Optional, List
from apps.accounts.models import User
from apps.payments.models import Payment, Payout, Settlement, PaymentDispute

def get_payment_by_id(payment_id) -> Optional[Payment]:
    return Payment.objects.filter(id=payment_id).select_related('shipment', 'payer').first()

def get_payment_by_idempotency_key(idempotency_key: str) -> Optional[Payment]:
    return Payment.objects.filter(idempotency_key=idempotency_key).select_related('shipment', 'payer').first()

def get_payments_for_user(user: User) -> List[Payment]:
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        return list(Payment.objects.all().select_related('shipment', 'payer'))
    elif user_role == 'SHIPPER':
        return list(Payment.objects.filter(payer=user).select_related('shipment', 'payer'))
    elif user_role == 'TRANSPORTER':
        return list(Payment.objects.filter(shipment__transporter=user).select_related('shipment', 'payer'))
    return []

def get_payouts_for_transporter(user: User) -> List[Payout]:
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        return list(Payout.objects.all().select_related('transporter', 'payment'))
    return list(Payout.objects.filter(transporter=user).select_related('transporter', 'payment'))

def get_settlements_for_user(user: User) -> List[Settlement]:
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        return list(Settlement.objects.all().select_related('shipment', 'payment', 'commission', 'payout'))
    elif user_role == 'TRANSPORTER':
        return list(Settlement.objects.filter(payout__transporter=user).select_related('shipment', 'payment', 'commission', 'payout'))
    elif user_role == 'SHIPPER':
        return list(Settlement.objects.filter(payment__payer=user).select_related('shipment', 'payment', 'commission', 'payout'))
    return []

def get_disputes_for_user(user: User) -> List[PaymentDispute]:
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        return list(PaymentDispute.objects.all().select_related('payment', 'raised_by'))
    return list(PaymentDispute.objects.filter(raised_by=user).select_related('payment', 'raised_by'))
