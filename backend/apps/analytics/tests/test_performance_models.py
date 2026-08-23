import pytest
from decimal import Decimal
from apps.accounts.models import User, RoleChoices
from apps.analytics.models import TransporterPerformance

@pytest.mark.django_db
def test_create_transporter_performance_model():
    transporter = User.objects.create_user(email='transporter_perf_m@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    perf = TransporterPerformance.objects.create(
        transporter=transporter,
        year=2026,
        month=8,
        period="2026-08",
        completed_trips=15,
        on_time_trips=14,
        on_time_delivery_rate=Decimal("93.33"),
        incident_count=1,
        incident_rate=Decimal("6.67"),
        total_distance_km=Decimal("7500.00"),
        total_fuel_liters=Decimal("1500.00"),
        fuel_efficiency=Decimal("5.00"),
        average_rating=Decimal("4.75"),
        rating_count=12
    )

    assert perf.transporter == transporter
    assert perf.period == "2026-08"
    assert perf.completed_trips == 15
    assert perf.fuel_efficiency == Decimal("5.00")
    assert "Performance:" in str(perf)
