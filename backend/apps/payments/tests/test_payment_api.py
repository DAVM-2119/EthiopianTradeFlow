import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.payments.models import Payment, PaymentStatusChoices

@pytest.mark.django_db
def test_payment_api_endpoints():
    now = timezone.now()
    shipper = User.objects.create_user(email='shipper_api_p@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_api_p@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    load = Load.objects.create(
        shipper=shipper, title="API Load", origin_city="Addis", destination_city="Modjo", weight=Decimal("10.00"), status=LoadStatusChoices.BOOKED,
        pickup_window_start=now, pickup_window_end=now, delivery_window_start=now, delivery_window_end=now
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("75000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, status=ShipmentStatusChoices.COMPLETED)

    client = APIClient()
    token_shipper = str(RefreshToken.for_user(shipper).access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')

    res_create = client.post('/api/v1/payments/', {
        'shipment_id': str(shipment.id),
        'amount': '75000.00',
        'currency': 'ETB',
        'idempotency_key': 'idemp-api-001'
    }, format='json')
    assert res_create.status_code == status.HTTP_201_CREATED
    payment_id = res_create.data['data']['id']

    res_init = client.post(f'/api/v1/payments/{payment_id}/initiate/')
    assert res_init.status_code == status.HTTP_200_OK

    res_conf = client.post(f'/api/v1/payments/{payment_id}/confirm/', {'provider_transaction_id': 'TX-CONF-API-001'}, format='json')
    assert res_conf.status_code == status.HTTP_200_OK
    assert res_conf.data['data']['status'] == PaymentStatusChoices.COMPLETED
