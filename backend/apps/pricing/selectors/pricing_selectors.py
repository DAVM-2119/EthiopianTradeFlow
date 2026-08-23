from django.utils import timezone
from apps.pricing.models import PriceQuote, ContractRate

def get_latest_price_quote(load_id):
    """
    Retrieves the most recent price quote for a load.
    """
    return PriceQuote.objects.filter(load_id=load_id).order_by('-created_at').first()


def get_price_quote_history(load_id):
    """
    Retrieves pricing quote history for a load.
    """
    return PriceQuote.objects.filter(load_id=load_id).order_by('-created_at')


def get_active_contract_rate(shipper, origin_city, destination_city):
    """
    Retrieves active contract rate locked for shipper on origin -> destination corridor.
    """
    now = timezone.now()
    return ContractRate.objects.filter(
        shipper=shipper,
        origin_city__iexact=origin_city.strip(),
        destination_city__iexact=destination_city.strip(),
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now
    ).order_by('-created_at').first()
