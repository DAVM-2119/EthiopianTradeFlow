import pytest
from decimal import Decimal
from apps.accounts.models import User, RoleChoices
from apps.analytics.models import TransporterPerformance
from apps.analytics.selectors import get_transporter_performance, get_transporter_performance_history, get_corridor_benchmark_data

@pytest.mark.django_db
def test_performance_selectors_and_corridor_benchmark():
    t1 = User.objects.create_user(email='t1_bench@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)
    t2 = User.objects.create_user(email='t2_bench@tradeflow.et', password='Password123!', role=RoleChoices.TRANSPORTER)

    TransporterPerformance.objects.create(
        transporter=t1, year=2026, month=8, period="2026-08", completed_trips=10,
        on_time_delivery_rate=Decimal("90.00"), incident_rate=Decimal("5.00"), fuel_efficiency=Decimal("5.00"), average_rating=Decimal("4.50")
    )
    TransporterPerformance.objects.create(
        transporter=t2, year=2026, month=8, period="2026-08", completed_trips=20,
        on_time_delivery_rate=Decimal("80.00"), incident_rate=Decimal("10.00"), fuel_efficiency=Decimal("4.00"), average_rating=Decimal("4.10")
    )

    p1 = get_transporter_performance(t1.id, 2026, 8)
    assert p1.completed_trips == 10

    hist = get_transporter_performance_history(t1.id)
    assert len(hist) == 1

    benchmark = get_corridor_benchmark_data(2026, 8)
    assert benchmark['total_transporters_benchmarked'] == 2
    assert benchmark['on_time_delivery_rate'] == 85.0
    assert benchmark['incident_rate'] == 7.5
    assert benchmark['fuel_efficiency'] == 4.5
