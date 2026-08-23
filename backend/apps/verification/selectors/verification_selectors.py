from apps.verification.models import Verification, VerificationHistory, VerificationStatusChoices

def get_user_verification(user):
    return Verification.objects.select_related('user').filter(user=user).first()


def get_pending_verifications():
    return Verification.objects.select_related('user').filter(status=VerificationStatusChoices.PENDING).order_by('submitted_at')


def get_verification_detail(verification_id):
    return Verification.objects.select_related('user').filter(id=verification_id).first()


def get_verification_history(verification_id):
    return VerificationHistory.objects.select_related('changed_by').filter(verification_id=verification_id).order_by('-created_at')
