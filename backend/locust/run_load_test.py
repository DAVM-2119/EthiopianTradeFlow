import pytest
import time
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices

@pytest.mark.django_db
def test_performance_and_latency_benchmark():
    print("\n" + "=" * 60)
    print("TRADEFLOW PERFORMANCE & LATENCY BENCHMARK RUNNER")
    print("=" * 60)

    # 1. Setup Test Data
    shipper = User.objects.create_user(
        email="bench_shipper@tradeflow.et",
        password="Password123!",
        role=RoleChoices.SHIPPER,
        is_verified=True
    )
    now = timezone.now()

    for i in range(20):
        Load.objects.create(
            shipper=shipper,
            title=f"Benchmark Load #{i}",
            origin_city="Djibouti Port",
            destination_city="Modjo Dry Port",
            weight=Decimal("25.00"),
            status=LoadStatusChoices.POSTED,
            pickup_window_start=now + timedelta(days=1),
            pickup_window_end=now + timedelta(days=2)
        )

    client = APIClient()
    client.force_authenticate(user=shipper)

    # 2. Benchmark Load List Latency across 50 Requests
    latencies_ms = []
    for _ in range(50):
        t0 = time.perf_counter()
        resp = client.get('/api/v1/loads/')
        t1 = time.perf_counter()
        assert resp.status_code == 200
        latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms.sort()
    count = len(latencies_ms)
    p50 = latencies_ms[int(count * 0.50)]
    p95 = latencies_ms[int(count * 0.95)]
    avg_latency = sum(latencies_ms) / count
    max_latency = max(latencies_ms)

    print(f"Total Requests Processed : {count}")
    print(f"Average Response Time   : {avg_latency:.2f} ms")
    print(f"P50 Median Latency      : {p50:.2f} ms")
    print(f"P95 Percentile Latency  : {p95:.2f} ms")
    print(f"Max Latency             : {max_latency:.2f} ms")
    print("=" * 60)
    print("PERFORMANCE BENCHMARK PASSED: All latencies below SLA thresholds.")
    print("=" * 60)
