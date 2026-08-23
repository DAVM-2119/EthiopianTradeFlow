from apps.matching.models import MatchRecommendation

def get_match_recommendation_by_id(match_id):
    return MatchRecommendation.objects.select_related('load', 'load__shipper', 'transporter').filter(id=match_id).first()


def get_active_matches_for_load(load):
    return MatchRecommendation.objects.select_related('transporter').filter(
        load=load,
        is_active=True
    ).order_by('rank')
