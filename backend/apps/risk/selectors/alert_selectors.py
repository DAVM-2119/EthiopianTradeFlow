from apps.risk.models import SecurityAlert, AlertStatusChoices

def get_security_alerts_for_shipment(shipment_id, active_only: bool = False):
    """
    Retrieves security alerts generated for a shipment.
    """
    qs = SecurityAlert.objects.filter(shipment_id=shipment_id).select_related('shipment', 'driver', 'risk_zone', 'incident', 'acknowledged_by')
    if active_only:
        qs = qs.filter(status=AlertStatusChoices.ACTIVE)
    return qs.order_by('-created_at')


def get_security_alerts_for_user(user, active_only: bool = False):
    """
    Retrieves security alerts relevant to a user (Shipper, Transporter, Driver, or Admin).
    """
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        qs = SecurityAlert.objects.all()
    else:
        qs = SecurityAlert.objects.filter(
            shipment__shipper=user
        ) | SecurityAlert.objects.filter(
            shipment__transporter=user
        ) | SecurityAlert.objects.filter(
            driver=user
        )

    qs = qs.select_related('shipment', 'driver', 'risk_zone', 'incident', 'acknowledged_by')
    if active_only:
        qs = qs.filter(status=AlertStatusChoices.ACTIVE)
    return qs.distinct().order_by('-created_at')
