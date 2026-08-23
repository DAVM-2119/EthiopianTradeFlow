from apps.marketplace.models import Bid, BidStatusChoices

def get_bid_by_id(bid_id):
    return Bid.objects.select_related('load', 'transporter').filter(id=bid_id).first()


def get_load_bids(load):
    return Bid.objects.select_related('transporter').filter(load=load).order_by('-amount')


def get_transporter_bids(transporter_user):
    return Bid.objects.select_related('load').filter(transporter=transporter_user).order_by('-created_at')


def get_active_bids_for_load(load):
    return Bid.objects.select_related('transporter').filter(load=load, status=BidStatusChoices.ACTIVE).order_by('-amount')
