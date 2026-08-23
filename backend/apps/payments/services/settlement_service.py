from django.db import transaction
from django.utils import timezone
from apps.payments.models import Payment, Commission, Payout, Settlement, SettlementStatusChoices

def create_settlement(*, payment: Payment, commission: Commission, payout: Payout) -> Settlement:
    """
    FR-10.2 Creates master financial reconciliation settlement record.
    """
    shipment = payment.shipment
    with transaction.atomic():
        settlement, created = Settlement.objects.update_or_create(
            shipment=shipment,
            defaults={
                'payment': payment,
                'commission': commission,
                'payout': payout,
                'gross_amount': commission.gross_amount,
                'commission_amount': commission.commission_amount,
                'net_transporter_amount': commission.net_amount,
                'status': SettlementStatusChoices.RECONCILED,
                'reconciled_at': timezone.now()
            }
        )
    return settlement
