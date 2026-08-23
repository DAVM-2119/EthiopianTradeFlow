import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.matching.models import MatchRecommendation

@pytest.mark.django_db
def test_matching_permissions_and_privacy_protection():
    s1 = User.objects.create_user(email='s1_mp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    s2 = User.objects.create_user(email='s2_mp@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    t1 = User.objects.create_user(email='t1_mp@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=s1,
        title="Privacy Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    rec = MatchRecommendation.objects.create(
        load=load,
        transporter=t1,
        rank=1,
        total_score=Decimal("90.00"),
        explanation="Test match",
        generated_at=now
    )

    client_s2 = APIClient()
    client_s2.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(s2).access_token}')

    list_url = reverse('load-matches-list-generate', kwargs={'load_id': load.id})
    list_resp = client_s2.get(list_url)
    assert list_resp.status_code == 403

    gen_resp = client_s2.post(list_url, format='json')
    assert gen_resp.status_code == 403

    detail_url = reverse('match-recommendation-detail', kwargs={'pk': rec.id})
    detail_resp = client_s2.get(detail_url)
    assert detail_resp.status_code == 403
