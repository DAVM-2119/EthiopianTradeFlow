import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.pricing.models import ContractRate, PricingAudit
from apps.pricing.services import calculate_and_save_price_quote
from apps.pricing.selectors import get_latest_price_quote

@pytest.mark.django_db
def test_calculate_and_save_price_quote_service():
    shipper = User.objects.create_user(email='shipper_p_srv@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Pricing Service Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("20.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    ContractRate.objects.create(
        shipper=shipper,
        origin_city="Addis Ababa",
        destination_city="Modjo",
        agreed_rate=Decimal("1000.00"),
        currency="ETB",
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        is_active=True,
        divergence_threshold_percent=Decimal("20.00")
    )

    quote = calculate_and_save_price_quote(load_id=load.id)
    assert quote is not None
    assert quote.load == load
    assert quote.divergence_warning is True
    assert "diverges from contract rate" in quote.divergence_notes

    latest = get_latest_price_quote(load.id)
    assert latest.id == quote.id

    audit = PricingAudit.objects.filter(price_quote=quote).first()
    assert audit is not None
    assert "base_price" in audit.output_snapshot
