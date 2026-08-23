import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.marketplace.services import create_load, update_load, post_load, cancel_load
from apps.core.exceptions import ConflictException, PermissionDeniedException

@pytest.mark.django_db
def test_load_lifecycle_services_workflow():
    shipper = User.objects.create_user(email='shipper_srv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load_data = {
        "title": "30 Tons Sesame Seeds",
        "origin_city": "Humera",
        "destination_city": "Djibouti Port",
        "weight": Decimal("30.00"),
        "pickup_window_start": now + timedelta(days=1),
        "pickup_window_end": now + timedelta(days=3)
    }

    load = create_load(shipper, load_data)
    assert load.status == LoadStatusChoices.DRAFT

    updated_load = update_load(load, shipper, {"title": "35 Tons Premium Sesame"})
    assert updated_load.title == "35 Tons Premium Sesame"

    posted_load = post_load(load, shipper)
    assert posted_load.status == LoadStatusChoices.POSTED

    with pytest.raises(ConflictException):
        post_load(posted_load, shipper)

    cancelled_load = cancel_load(posted_load, shipper)
    assert cancelled_load.status == LoadStatusChoices.CANCELLED

    with pytest.raises(ConflictException):
        post_load(cancelled_load, shipper)
