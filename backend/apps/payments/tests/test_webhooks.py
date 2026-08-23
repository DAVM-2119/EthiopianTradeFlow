import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import Payment, PaymentStatusChoices

@pytest.mark.django_db
def test_webhook_processing_and_idempotency():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_wh@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_wh@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="Webhook Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("60000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    payment = Payment.objects.create(
        shipment=shipment, payer=shipper, amount=Decimal("60000.00"), currency="ETB",
        status=PaymentStatusChoices.INITIATED, provider_transaction_id="TX-WH-001", idempotency_key="wh-key-001"
    )

    client = APIClient()

    res1 = client.post('/api/v1/payments/webhooks/provider/?provider=MOCK', {
        'transaction_id': 'TX-WH-001',
        'event_type': 'payment.success',
        'idempotency_key': 'wh-key-001'
    }, format='json')
    assert res1.status_code == status.HTTP_200_OK
    assert res1.data['data']['status'] == 'PROCESSED'

    payment.refresh_from_db()
    assert payment.status == PaymentStatusChoices.COMPLETED

    res2 = client.post('/api/v1/payments/webhooks/provider/?provider=MOCK', {
        'transaction_id': 'TX-WH-001',
        'event_type': 'payment.success',
        'idempotency_key': 'wh-key-001'
    }, format='json')
    assert res2.status_code == status.HTTP_200_OK
    assert res2.data['data']['status'] == 'IGNORED'
