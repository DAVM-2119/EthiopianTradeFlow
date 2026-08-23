import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices, Bid, BidStatusChoices
from apps.marketplace.services import accept_bid
from apps.core.exceptions import ConflictException

@pytest.mark.django_db
def test_select_for_update_double_acceptance_prevention():
    shipper = User.objects.create_user(email='shipper_conc@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t1 = User.objects.create_user(email='t1_conc@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t2 = User.objects.create_user(email='t2_conc@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Load for Concurrency Test",
        origin_city="Djibouti",
        destination_city="Addis Ababa",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    b1 = Bid.objects.create(load=load, transporter=t1, amount=Decimal("100000.00"), status=BidStatusChoices.ACTIVE)
    b2 = Bid.objects.create(load=load, transporter=t2, amount=Decimal("95000.00"), status=BidStatusChoices.ACTIVE)

    accepted1 = accept_bid(bid_id=b1.id, load_owner_user=shipper)
    assert accepted1.status == BidStatusChoices.ACCEPTED

    b2.refresh_from_db()
    assert b2.status == BidStatusChoices.REJECTED

    with pytest.raises(ConflictException):
        accept_bid(bid_id=b2.id, load_owner_user=shipper)
