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
from apps.marketplace.models import Load, LoadStatusChoices

@pytest.mark.django_db
def test_matching_api_end_to_end_workflow():
    shipper = User.objects.create_user(email='shipper_mapi@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_mapi@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter, city="Addis Ababa")
    v = Vehicle.objects.create(transporter=t_prof, registration_number="3-MAPI-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.INSURANCE, document_number="INS", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=transporter, status=VerificationStatusChoices.VERIFIED)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Freight Load for API Test",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    s_client = APIClient()
    s_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')

    list_url = reverse('load-matches-list-generate', kwargs={'load_id': load.id})
    gen_resp = s_client.post(list_url, format='json')
    assert gen_resp.status_code == 200
    results = gen_resp.json()['data']
    assert len(results) == 1
    match_id = results[0]['id']

    list_resp = s_client.get(list_url)
    assert list_resp.status_code == 200
    assert len(list_resp.json()['data']) == 1

    detail_url = reverse('match-recommendation-detail', kwargs={'pk': match_id})
    detail_resp = s_client.get(detail_url)
    assert detail_resp.status_code == 200
    assert float(detail_resp.json()['data']['total_score']) > 0
