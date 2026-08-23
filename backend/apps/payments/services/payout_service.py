from django.db import transaction
from django.utils import timezone
from apps.core.exceptions import ValidationException, NotFoundException
from apps.payments.models import Payment, Payout, PayoutStatusChoices, Commission
from apps.payments.providers import get_payment_provider

def create_payout(*, payment: Payment, commission: Commission) -> Payout:
    """
    FR-10.2 Creates scheduled payout for the shipment's transporter.
    """
    transporter = payment.shipment.transporter
    with transaction.atomic():
        payout, created = Payout.objects.get_or_create(
            payment=payment,
            defaults={
                'transporter': transporter,
                'gross_amount': commission.gross_amount,
                'commission_amount': commission.commission_amount,
                'net_amount': commission.net_amount,
                'status': PayoutStatusChoices.SCHEDULED,
                'scheduled_at': timezone.now()
            }
        )
    return payout


def process_payout(*, payout_id: str) -> Payout:
    """
    Executes transporter payout via provider interface.
    """
    payout = Payout.objects.filter(id=payout_id).select_related('payment').first()
    if not payout:
        raise NotFoundException("Payout not found.")

    if payout.status == PayoutStatusChoices.COMPLETED:
        return payout

    provider = get_payment_provider(payout.payment.provider)
    res = provider.initiate_payout(payout=payout)

    with transaction.atomic():
        if res.get('success'):
            payout.status = PayoutStatusChoices.COMPLETED
            payout.processed_at = timezone.now()
            payout.provider_transaction_id = res.get('provider_transaction_id')
        else:
            payout.status = PayoutStatusChoices.FAILED
            payout.failure_reason = res.get('message', 'Payout processing failed.')
        payout.save()

    return payout
