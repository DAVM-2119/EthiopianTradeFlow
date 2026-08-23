import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from apps.accounts.models import User, RoleChoices
from apps.profiles.models import TransporterProfile
from apps.marketplace.models import Load, LoadStatusChoices
from apps.matching.services import calculate_candidate_scores

@pytest.mark.django_db
def test_deterministic_scoring_calculations():
    shipper = User.objects.create_user(email='shipper_ss@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    transporter = User.objects.create_user(email='transporter_ss@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t_prof, _ = TransporterProfile.objects.get_or_create(user=transporter, city="Addis Ababa")

    now = timezone.now()
    load = Load.objects.create(
        shipper=shipper,
        title="Djibouti Freight Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    scores = calculate_candidate_scores(transporter, load)

    assert scores['proximity_score'] == Decimal('100.00')
    assert scores['total_score'] > 0
    assert 'total_score' in scores
    assert scores['algorithm_version'] == 'v1'
