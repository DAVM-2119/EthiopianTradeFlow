import pytest
from decimal import Decimal
from datetime import timedelta, date
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices

@pytest.mark.django_db
def test_full_bidding_and_booking_api_workflow():
    shipper = User.objects.create_user(email='shipper_api_wf@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_api_wf@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter)
    v = Vehicle.objects.create(transporter=t_prof, registration_number="3-API-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-API", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-API", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-API", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=transporter, status=VerificationStatusChoices.VERIFIED)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Djibouti Freight Load",
        origin_city="Djibouti Port",
        destination_city="Modjo Dry Port",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    t_client = APIClient()
    t_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(transporter).access_token}')

    create_bid_url = reverse('load-bids-list-create', kwargs={'load_id': load.id})
    bid_resp = t_client.post(create_bid_url, {
        "amount": "130000.00",
        "message": "Available for immediate pickup"
    }, format='json')
    assert bid_resp.status_code == 201
    bid_id = bid_resp.json()['id']
    assert bid_resp.json()['status'] == BidStatusChoices.ACTIVE

    detail_url = reverse('bid-detail', kwargs={'pk': bid_id})
    patch_resp = t_client.patch(detail_url, {"amount": "125000.00"}, format='json')
    assert patch_resp.status_code == 200
    assert patch_resp.json()['amount'] == "125000.00"

    s_client = APIClient()
    s_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')
    bids_list_resp = s_client.get(create_bid_url)
    assert bids_list_resp.status_code == 200
    assert len(bids_list_resp.json()['results']) == 1

    accept_url = reverse('bid-accept', kwargs={'pk': bid_id})
    accept_resp = s_client.post(accept_url, format='json')
    assert accept_resp.status_code == 200
    assert accept_resp.json()['data']['status'] == BidStatusChoices.ACCEPTED

    load.refresh_from_db()
    assert load.status == LoadStatusChoices.BOOKED
