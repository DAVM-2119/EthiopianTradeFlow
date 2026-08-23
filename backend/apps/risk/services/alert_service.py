from django.utils import timezone
from apps.core.exceptions import NotFoundException
from apps.risk.models import SecurityAlert, AlertStatusChoices

def acknowledge_alert(alert_id, *, user) -> SecurityAlert:
    """
    Marks a security alert as acknowledged by user.
    """
    alert = SecurityAlert.objects.filter(id=alert_id).first()
    if not alert:
        raise NotFoundException("SecurityAlert not found.")

    alert.status = AlertStatusChoices.ACKNOWLEDGED
    alert.acknowledged_at = timezone.now()
    alert.acknowledged_by = user
    alert.save()
    return alert


def resolve_alert(alert_id) -> SecurityAlert:
    """
    Marks a security alert as resolved.
    """
    alert = SecurityAlert.objects.filter(id=alert_id).first()
    if not alert:
        raise NotFoundException("SecurityAlert not found.")

    alert.status = AlertStatusChoices.RESOLVED
    alert.save()
    return alert


def dismiss_alert(alert_id) -> SecurityAlert:
    """
    Marks a security alert as dismissed.
    """
    alert = SecurityAlert.objects.filter(id=alert_id).first()
    if not alert:
        raise NotFoundException("SecurityAlert not found.")

    alert.status = AlertStatusChoices.DISMISSED
    alert.save()
    return alert
