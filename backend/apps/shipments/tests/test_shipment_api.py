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
from apps.marketplace.services import create_bid, accept_bid
from apps.shipments.models import ShipmentStatusChoices

@pytest.mark.django_db
def test_full_shipment_api_lifecycle_workflow():
    shipper = User.objects.create_user(email='shipper_sapi@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_sapi@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    driver = User.objects.create_user(email='driver_sapi@tradeflow.et', password='Password123!', role=RoleChoices.DRIVER)

    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter, city="Addis Ababa")
    v = Vehicle.objects.create(transporter=t_prof, registration_number="3-SAPI-ET", vehicle_type=VehicleTypeChoices.HEAVY_TRUCK, capacity=Decimal("30.00"))
    tomorrow = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.INSURANCE, document_number="INS", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG", status=DocumentStatusChoices.VALID, expiry_date=tomorrow)
    Verification.objects.create(user=transporter, status=VerificationStatusChoices.VERIFIED)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Freight Load for Shipment API",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("30.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = create_bid(transporter_user=transporter, load_id=load.id, validated_data={"amount": Decimal("80000.00")})
    accept_bid(bid_id=bid.id, load_owner_user=shipper)

    t_client = APIClient()
    t_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(transporter).access_token}')

    list_resp = t_client.get(reverse('shipment-list'))
    assert list_resp.status_code == 200
    shipments = list_resp.json()['results']
    assert len(shipments) == 1
    shipment_id = shipments[0]['id']

    assign_url = reverse('shipment-assign', kwargs={'pk': shipment_id})
    assign_resp = t_client.post(assign_url, {
        "vehicle_id": str(v.id),
        "driver_id": str(driver.id)
    }, format='json')
    assert assign_resp.status_code == 200
    assert assign_resp.json()['data']['status'] == ShipmentStatusChoices.ASSIGNED

    trans_url = reverse('shipment-transition', kwargs={'pk': shipment_id})
    t_client.post(trans_url, {"status": ShipmentStatusChoices.PICKUP_READY}, format='json')
    t_client.post(trans_url, {"status": ShipmentStatusChoices.IN_TRANSIT}, format='json')
    deliv_resp = t_client.post(trans_url, {"status": ShipmentStatusChoices.DELIVERED}, format='json')
    assert deliv_resp.status_code == 200

    pod_url = reverse('shipment-proof-of-delivery', kwargs={'pk': shipment_id})
    pod_resp = t_client.post(pod_url, {
        "receiver_name": "Tadesse Hailu",
        "delivery_timestamp": now.isoformat(),
        "notes": "Delivered in full"
    }, format='json')
    assert pod_resp.status_code == 200

    s_client = APIClient()
    s_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(shipper).access_token}')

    comp_url = reverse('shipment-complete', kwargs={'pk': shipment_id})
    comp_resp = s_client.post(comp_url, format='json')
    assert comp_resp.status_code == 200
    assert comp_resp.json()['data']['status'] == ShipmentStatusChoices.COMPLETED

    events_url = reverse('shipment-events', kwargs={'pk': shipment_id})
    events_resp = s_client.get(events_url)
    assert events_resp.status_code == 200
    assert len(events_resp.json()['results']) >= 5
