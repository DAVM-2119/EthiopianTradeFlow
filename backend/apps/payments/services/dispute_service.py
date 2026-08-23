from decimal import Decimal
from typing import Optional
from django.db import transaction
from django.utils import timezone
from apps.core.exceptions import NotFoundException, ValidationException, PermissionDeniedException
from apps.accounts.models import User
from apps.payments.models import Payment, PaymentDispute, DisputeStatusChoices, DisputeReasonChoices

def raise_dispute(*, payment_id: str, raised_by_id: str, reason: str, description: str, disputed_amount: Optional[Decimal] = None) -> PaymentDispute:
    """
    FR-10.3 Raises a payment discrepancy dispute report.
    """
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        raise NotFoundException("Payment not found.")

    user = User.objects.filter(id=raised_by_id).first()
    if not user:
        raise NotFoundException("User not found.")

    dis_amt = disputed_amount if disputed_amount is not None else payment.amount

    with transaction.atomic():
        dispute = PaymentDispute.objects.create(
            payment=payment,
            raised_by=user,
            reason=reason,
            description=description,
            disputed_amount=dis_amt,
            status=DisputeStatusChoices.OPEN
        )

    return dispute


def resolve_dispute(*, dispute_id: str, resolved_by_id: str, resolution_status: str, resolution_notes: str) -> PaymentDispute:
    """
    FR-10.3 Admin dispute resolution workflow.
    """
    dispute = PaymentDispute.objects.filter(id=dispute_id).first()
    if not dispute:
        raise NotFoundException("Payment dispute not found.")

    admin_user = User.objects.filter(id=resolved_by_id).first()
    if not admin_user or not (admin_user.is_staff or getattr(admin_user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("Only system administrators can resolve payment disputes.")

    if resolution_status not in [DisputeStatusChoices.RESOLVED, DisputeStatusChoices.REJECTED, DisputeStatusChoices.CANCELLED]:
        raise ValidationException(f"Invalid resolution status: {resolution_status}")

    with transaction.atomic():
        dispute.status = resolution_status
        dispute.resolution_notes = resolution_notes
        dispute.resolved_by = admin_user
        dispute.resolved_at = timezone.now()
        dispute.save()

    return dispute
