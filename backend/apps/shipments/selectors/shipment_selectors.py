from django.db import models
from apps.shipments.models import Shipment, ShipmentEvent, ProofOfDelivery

def get_shipment_by_id(shipment_id):
    return Shipment.objects.select_related(
        'load', 'bid', 'shipper', 'transporter', 'vehicle', 'driver', 'cancelled_by', 'proof_of_delivery'
    ).filter(id=shipment_id).first()


def get_user_shipments(user, status_filter=None):
    qs = Shipment.objects.select_related('load', 'shipper', 'transporter', 'vehicle', 'driver')

    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        pass
    elif getattr(user, 'role', '') == 'SHIPPER':
        qs = qs.filter(shipper=user)
    elif getattr(user, 'role', '') == 'TRANSPORTER':
        qs = qs.filter(transporter=user)
    elif getattr(user, 'role', '') == 'DRIVER':
        qs = qs.filter(driver=user)
    else:
        qs = qs.filter(models.Q(shipper=user) | models.Q(transporter=user) | models.Q(driver=user))

    if status_filter:
        qs = qs.filter(status=status_filter)

    return qs.order_by('-created_at')


def get_shipment_events(shipment):
    return ShipmentEvent.objects.select_related('created_by').filter(shipment=shipment).order_by('created_at')


def get_proof_of_delivery(shipment):
    return ProofOfDelivery.objects.select_related('submitted_by').filter(shipment=shipment).first()
