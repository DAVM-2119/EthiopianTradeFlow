import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, CargoTypeChoices

@pytest.mark.django_db
def test_load_creation_defaults_and_validation():
    shipper = User.objects.create_user(email='shipper_m@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()
    pickup_start = now + timedelta(days=1)
    pickup_end = now + timedelta(days=2)

    load = Load.objects.create(
        shipper=shipper,
        title="20 Tons Coffee Beans",
        origin_city="Modjo Dry Port",
        destination_city="Djibouti Port",
        cargo_type=CargoTypeChoices.CONTAINERIZED,
        weight=Decimal("20.00"),
        pickup_window_start=pickup_start,
        pickup_window_end=pickup_end
    )

    assert load.status == LoadStatusChoices.DRAFT
    assert load.weight == Decimal("20.00")
    assert str(load.id) is not None


@pytest.mark.django_db
def test_invalid_pickup_window_raises_validation_error():
    shipper = User.objects.create_user(email='shipper_val@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()
    pickup_start = now + timedelta(days=2)
    pickup_end = now + timedelta(days=1)

    load = Load(
        shipper=shipper,
        title="Invalid Window Load",
        origin_city="Addis Ababa",
        destination_city="Hawassa",
        weight=Decimal("10.00"),
        pickup_window_start=pickup_start,
        pickup_window_end=pickup_end
    )
    with pytest.raises(ValidationError):
        load.clean()
