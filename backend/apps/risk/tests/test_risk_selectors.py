import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.risk.models import RiskZone, IncidentReport, IncidentTypeChoices, IncidentStatusChoices
from apps.risk.selectors import get_active_risk_zones, get_risk_zones_in_proximity, get_active_incidents

@pytest.mark.django_db
def test_risk_selectors_temporal_and_proximity_filtering():
    now = timezone.now()

    z_active = RiskZone.objects.create(
        name="Active Zone", latitude=Decimal("9.000000"), longitude=Decimal("38.700000"),
        radius_km=Decimal("10.00"), is_active=True, effective_from=now - timedelta(days=1)
    )

    z_inactive = RiskZone.objects.create(
        name="Inactive Zone", latitude=Decimal("9.100000"), longitude=Decimal("38.750000"),
        radius_km=Decimal("10.00"), is_active=False
    )

    z_expired = RiskZone.objects.create(
        name="Expired Zone", latitude=Decimal("9.200000"), longitude=Decimal("38.800000"),
        radius_km=Decimal("10.00"), is_active=True, effective_from=now - timedelta(days=5), effective_until=now - timedelta(days=1)
    )

    active_zones = list(get_active_risk_zones())
    assert z_active in active_zones
    assert z_inactive not in active_zones
    assert z_expired not in active_zones

    prox_zones = get_risk_zones_in_proximity(Decimal("9.010000"), Decimal("38.710000"), max_distance_km=20.0)
    assert len(prox_zones) == 1
    assert prox_zones[0][0] == z_active
