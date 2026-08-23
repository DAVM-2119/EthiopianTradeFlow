import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.matching.models import MatchRecommendation

@pytest.mark.django_db
def test_match_recommendation_model_defaults_and_constraints():
    shipper = User.objects.create_user(email='shipper_mm@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_mm@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Test Load for Matching",
        origin_city="Addis Ababa",
        destination_city="Hawassa",
        weight=Decimal("10.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    rec = MatchRecommendation.objects.create(
        load=load,
        transporter=transporter,
        rank=1,
        total_score=Decimal("85.50"),
        explanation="Test explanation",
        generated_at=now
    )

    assert rec.rank == 1
    assert rec.total_score == Decimal("85.50")
    assert rec.is_active is True
    assert rec.algorithm_version == 'v1'
