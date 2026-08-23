import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.customs.models import CustomsDocumentTypeChoices

@pytest.mark.django_db
def test_customs_api_endpoints():
    shipper = User.objects.create_user(email='shipper_cust_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_cust_api@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_cust_api@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)
    customs_staff = User.objects.create_user(email='staff_cust_api@tradeflow.et', password='Password123!', role=RoleChoices.CUSTOMS_STAFF)
    unrelated_user = User.objects.create_user(email='unrelated_cust_api@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Customs API Load",
        origin_city="Djibouti Port",
        destination_city="Modjo",
        weight=Decimal("50.00"),
        status=LoadStatusChoices.BOOKED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )
    bid = Bid.objects.create(load=load, transporter=transporter, amount=Decimal("120000.00"), status=BidStatusChoices.ACCEPTED)
    shipment = Shipment.objects.create(load=load, bid=bid, shipper=shipper, transporter=transporter, driver=driver, status=ShipmentStatusChoices.IN_TRANSIT)

    client = APIClient()
    token_shipper = str(RefreshToken.for_user(shipper).access_token)
    token_staff = str(RefreshToken.for_user(customs_staff).access_token)
    token_unrelated = str(RefreshToken.for_user(unrelated_user).access_token)

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_unrelated}')
    res_unauth = client.get(f'/api/v1/shipments/{shipment.id}/customs/documents/')
    assert res_unauth.status_code == status.HTTP_403_FORBIDDEN

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_shipper}')
    doc_types = [
        (CustomsDocumentTypeChoices.COMMERCIAL_INVOICE, "inv.pdf", "100.00", "250000.00"),
        (CustomsDocumentTypeChoices.PACKING_LIST, "pack.pdf", "100.00", None),
        (CustomsDocumentTypeChoices.BILL_OF_LADING, "bol.pdf", None, None),
        (CustomsDocumentTypeChoices.CERTIFICATE_OF_ORIGIN, "coo.pdf", None, None),
    ]

    doc_ids = []
    for dtype, fname, qty, val in doc_types:
        f = SimpleUploadedFile(fname, b"PDF content", content_type="application/pdf")
        payload = {"document_type": dtype, "file": f}
        if qty: payload["quantity"] = qty
        if val: payload["declared_value"] = val
        res_up = client.post(f'/api/v1/shipments/{shipment.id}/customs/documents/', payload, format='multipart')
        assert res_up.status_code == status.HTTP_201_CREATED
        doc_ids.append(res_up.data['data']['id'])

    res_list = client.get(f'/api/v1/shipments/{shipment.id}/customs/documents/')
    assert res_list.status_code == status.HTTP_200_OK
    assert len(res_list.data['data']) == 4

    res_det = client.get(f'/api/v1/customs/documents/{doc_ids[0]}/')
    assert res_det.status_code == status.HTTP_200_OK
    assert res_det.data['data']['id'] == doc_ids[0]

    res_val = client.post(f'/api/v1/shipments/{shipment.id}/customs/validate/')
    assert res_val.status_code == status.HTTP_200_OK
    assert res_val.data['data']['valid'] is True

    res_sub = client.post(f'/api/v1/shipments/{shipment.id}/customs/submit/')
    assert res_sub.status_code == status.HTTP_200_OK
    assert res_sub.data['data']['status'] == 'SUBMITTED'

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_staff}')
    res_stat = client.post(f'/api/v1/shipments/{shipment.id}/customs/status/', {'status': 'CLEARED'}, format='json')
    assert res_stat.status_code == status.HTTP_200_OK
    assert res_stat.data['data']['status'] == 'CLEARED'
