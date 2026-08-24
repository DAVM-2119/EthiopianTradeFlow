import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.marketplace.models import Load, Bid, BidStatusChoices, LoadStatusChoices
from apps.shipments.models import Shipment, ShipmentStatusChoices
from apps.eta.services import calculate_and_save_eta
from apps.eta.predictors import RuleBasedETAPredictor
from ml.eta.predictor import MLETAPredictor

from datetime import date, timedelta
from decimal import Decimal
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleDocument, VehicleTypeChoices, DocumentTypeChoices, DocumentStatusChoices
from apps.verification.models import Verification, VerificationStatusChoices

User = get_user_model()

@pytest.mark.django_db
def test_full_shipper_to_delivery_end_to_end_flow():
    # 1. Create Users, Profiles, & Vehicle Documents
    shipper = User.objects.create_user(
        email="shipper_flow@tradeflow.eth",
        password="Password123!",
        role="SHIPPER",
        is_verified=True
    )
    transporter = User.objects.create_user(
        email="transporter_flow@tradeflow.eth",
        password="Password123!",
        role="TRANSPORTER",
        is_verified=True
    )
    driver = User.objects.create_user(
        email="driver_flow@tradeflow.eth",
        password="Password123!",
        role="DRIVER",
        is_verified=True
    )

    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter)
    v = Vehicle.objects.create(
        transporter=t_prof,
        registration_number="3-FLOW-ET",
        vehicle_type=VehicleTypeChoices.HEAVY_TRUCK,
        capacity=Decimal("30.00")
    )
    expiry = date.today() + timedelta(days=365)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.INSURANCE, document_number="INS-FLOW", status=DocumentStatusChoices.VALID, expiry_date=expiry)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.ROADWORTHINESS, document_number="RW-FLOW", status=DocumentStatusChoices.VALID, expiry_date=expiry)
    VehicleDocument.objects.create(vehicle=v, document_type=DocumentTypeChoices.REGISTRATION, document_number="REG-FLOW", status=DocumentStatusChoices.VALID, expiry_date=expiry)
    Verification.objects.create(user=transporter, status=VerificationStatusChoices.VERIFIED)

    client = APIClient()

    # 2. Shipper Creates Load & Posts
    client.force_authenticate(user=shipper)
    load_resp = client.post('/api/v1/loads/', {
        "title": "Ethio-Djibouti Container Freight",
        "origin_city": "Djibouti Port",
        "destination_city": "Modjo Dry Port",
        "cargo_type": "CONTAINERIZED",
        "weight": "28.50",
        "pickup_window_start": "2026-09-01T08:00:00Z",
        "pickup_window_end": "2026-09-03T18:00:00Z"
    }, format='json')
    assert load_resp.status_code == status.HTTP_201_CREATED
    load_id = load_resp.data['id']

    # Post load to marketplace
    post_resp = client.post(f'/api/v1/loads/{load_id}/post/')
    assert post_resp.status_code == status.HTTP_200_OK

    # 3. Transporter Submits Bid
    client.force_authenticate(user=transporter)
    bid_resp = client.post(f'/api/v1/loads/{load_id}/bids/', {
        "amount": "80000.00",
        "notes": "Fast transit guaranteed"
    })
    assert bid_resp.status_code == status.HTTP_201_CREATED
    bid_id = bid_resp.data['id']

    # 4. Shipper Accepts Bid (Creates Shipment)
    client.force_authenticate(user=shipper)
    accept_resp = client.post(f'/api/v1/loads/bids/{bid_id}/accept/')
    assert accept_resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    shipment = Shipment.objects.filter(load_id=load_id).first()
    assert shipment is not None
    assert shipment.status in (ShipmentStatusChoices.BOOKED, ShipmentStatusChoices.ASSIGNED)

    # 5. Assign Driver & Vehicle Resources
    client.force_authenticate(user=transporter)
    assign_resp = client.post(f'/api/v1/shipments/{shipment.id}/assign/', {
        "vehicle_id": str(v.id),
        "driver_id": str(driver.id)
    }, format='json')
    assert assign_resp.status_code == status.HTTP_200_OK

    # 6. Pickup Ready & Driver Begins Transit
    client.force_authenticate(user=transporter)
    pickup_resp = client.post(f'/api/v1/shipments/{shipment.id}/transition/', {
        "status": "PICKUP_READY"
    }, format='json')
    assert pickup_resp.status_code == status.HTTP_200_OK

    client.force_authenticate(user=driver)
    transit_resp = client.post(f'/api/v1/shipments/{shipment.id}/transition/', {
        "status": "IN_TRANSIT"
    }, format='json')
    assert transit_resp.status_code == status.HTTP_200_OK

    track_resp = client.post('/api/v1/tracking/events/', {
        "shipment": str(shipment.id),
        "latitude": 11.5883,
        "longitude": 43.1450,
        "speed": 64.5,
        "heading": 240.0,
        "recorded_at": timezone.now().isoformat(),
        "event_id": "flow-gps-evt-001"
    }, format='json')
    assert track_resp.status_code == status.HTTP_201_CREATED

    # 7. Calculate ETA via ML & Rule Fallback
    eta_ml = calculate_and_save_eta(shipment_id=shipment.id, predictor=MLETAPredictor())
    assert eta_ml is not None
    assert eta_ml.estimated_arrival is not None

    eta_rule = calculate_and_save_eta(shipment_id=shipment.id, predictor=RuleBasedETAPredictor())
    assert eta_rule is not None

    # 8. Digital Proof of Delivery
    client.force_authenticate(user=driver)
    delivered_resp = client.post(f'/api/v1/shipments/{shipment.id}/transition/', {
        "status": "DELIVERED"
    }, format='json')
    assert delivered_resp.status_code == status.HTTP_200_OK

    pod_resp = client.post(f'/api/v1/shipments/{shipment.id}/proof-of-delivery/', {
        "receiver_name": "Abebe Kebede (Modjo Terminal Manager)",
        "delivery_timestamp": timezone.now().isoformat(),
        "notes": "Cargo intact, zero damage."
    }, format='json')
    assert pod_resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    shipment.refresh_from_db()
    assert shipment.status == ShipmentStatusChoices.DELIVERED
