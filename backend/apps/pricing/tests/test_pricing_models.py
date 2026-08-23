import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.pricing.models import PriceQuote, ContractRate, PricingAudit

@pytest.mark.django_db
def test_create_pricing_models():
    shipper = User.objects.create_user(email='shipper_p_mod@tradeflow.et', password='Password123!', role=RoleChoices.SHIPPER)
    now = timezone.now()

    load = Load.objects.create(
        shipper=shipper,
        title="Pricing Test Load",
        origin_city="Addis Ababa",
        destination_city="Modjo",
        weight=Decimal("15.00"),
        status=LoadStatusChoices.POSTED,
        pickup_window_start=now + timedelta(days=1),
        pickup_window_end=now + timedelta(days=2)
    )

    quote = PriceQuote.objects.create(
        load=load,
        base_price=Decimal("10000.00"),
        demand_multiplier=Decimal("1.15"),
        fuel_multiplier=Decimal("1.05"),
        congestion_multiplier=Decimal("1.00"),
        calculated_price=Decimal("12075.00"),
        final_price=Decimal("12075.00"),
        currency="ETB",
        valid_from=now,
        valid_until=now + timedelta(hours=24)
    )

    contract = ContractRate.objects.create(
        shipper=shipper,
        origin_city="Addis Ababa",
        destination_city="Modjo",
        agreed_rate=Decimal("9500.00"),
        currency="ETB",
        valid_from=now,
        valid_until=now + timedelta(days=30),
        is_active=True
    )

    audit = PricingAudit.objects.create(
        price_quote=quote,
        input_snapshot={"base_rate": 10000},
        output_snapshot={"final_price": 12075},
        algorithm_version="pricing-v1"
    )

    assert quote.load == load
    assert "Price Quote for Load" in str(quote)
    assert contract.agreed_rate == Decimal("9500.00")
    assert audit.price_quote == quote
