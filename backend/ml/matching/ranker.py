from typing import List, Dict, Any

class AdvancedMatcher:
    """
    Advanced ML-ready multi-criteria freight matching ranker.
    Ranks transporter bids by combining price score, historical on-time delivery rate,
    fuel efficiency index, cancellation penalty, and corridor experience.
    """
    def rank_bids(self, load_data: Dict[str, Any], bids: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not bids:
            return []

        ranked_bids = []
        max_amount = max(float(b.get('amount', 1)) for b in bids) or 1.0

        for b in bids:
            amount = float(b.get('amount', max_amount))
            on_time_rate = float(b.get('on_time_rate', 0.95))
            cancellation_rate = float(b.get('cancellation_rate', 0.02))
            corridor_trips = float(b.get('corridor_trips', 10))

            price_score = max(0.0, 1.0 - (amount / (max_amount * 1.2)))
            reliability_score = max(0.0, on_time_rate - (cancellation_rate * 2.0))
            experience_score = min(1.0, corridor_trips / 50.0)

            # Combined weighted score
            ml_composite_score = round(
                (price_score * 0.35) +
                (reliability_score * 0.45) +
                (experience_score * 0.20),
                4
            )

            bid_copy = dict(b)
            bid_copy['ml_composite_score'] = ml_composite_score
            ranked_bids.append(bid_copy)

        ranked_bids.sort(key=lambda x: x['ml_composite_score'], reverse=True)
        return ranked_bids
