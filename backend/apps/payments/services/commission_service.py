from decimal import Decimal
from django.db import transaction
from apps.payments.models import Payment, Commission

def calculate_commission(*, payment: Payment, rate_percent: Decimal = Decimal('5.00')) -> Commission:
    """
    FR-10.2 Persists platform commission calculation for a confirmed payment.
    Commission = rate_percent % of gross payment.
    Net Transporter Amount = gross payment - commission.
    """
    gross = payment.amount
    comm_amount = round((gross * rate_percent) / Decimal('100.00'), 2)
    net_amount = gross - comm_amount

    with transaction.atomic():
        comm, _ = Commission.objects.update_or_create(
            payment=payment,
            defaults={
                'rate': rate_percent,
                'gross_amount': gross,
                'commission_amount': comm_amount,
                'net_amount': net_amount,
                'calculation_version': 'v1'
            }
        )
    return comm
