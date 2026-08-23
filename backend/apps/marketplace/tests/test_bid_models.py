import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices

@pytest.mark.django_db
def test_bid_model_defaults_and_constraints():
    shipper = User.objects.create_user(email='shipper_bm@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_bm@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Test Load",
        origin_city="Addis Ababa",
        destination_city="Hawassa",
        weight=Decimal("10.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    bid = Bid.objects.create(
        load=load,
        transporter=transporter,
        amount=Decimal("15000.00"),
        currency="ETB"
    )

    assert bid.status == BidStatusChoices.ACTIVE
    assert bid.amount == Decimal("15000.00")
    assert bid.currency == "ETB"
    assert str(bid.id) is not None
