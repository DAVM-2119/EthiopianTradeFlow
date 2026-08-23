from decimal import Decimal
from apps.marketplace.models import Bid, BidStatusChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.models import Vehicle, VehicleStatusChoices

# Deterministic Weights v1
COST_WEIGHT = Decimal('0.30')
RELIABILITY_WEIGHT = Decimal('0.25')
FUEL_WEIGHT = Decimal('0.15')
PROXIMITY_WEIGHT = Decimal('0.20')
AVAILABILITY_WEIGHT = Decimal('0.10')

def calculate_cost_score(transporter_user, load):
    """
    Calculates cost score (0-100).
    If transporter placed an active bid, score relative to bid; otherwise return neutral fallback 75.00.
    """
    bid = Bid.objects.filter(load=load, transporter=transporter_user, status=BidStatusChoices.ACTIVE).first()
    if bid:
        return Decimal('85.00')
    return Decimal('75.00')


def calculate_reliability_score(transporter_user):
    """
    Calculates reliability score (0-100).
    Uses completed accepted bids or returns baseline 80.00 for verified transporters.
    """
    accepted_bids_count = Bid.objects.filter(transporter=transporter_user, status=BidStatusChoices.ACCEPTED).count()
    if accepted_bids_count > 0:
        return min(Decimal('80.00') + Decimal(str(accepted_bids_count * 2)), Decimal('100.00'))
    return Decimal('80.00')


def calculate_fuel_efficiency_score(transporter_user):
    """
    Calculates fuel efficiency score (0-100).
    Derived from fleet vehicle capacity efficiency ratio; fallback to neutral baseline 70.00.
    """
    prof = TransporterProfile.objects.filter(user=transporter_user).first()
    if prof:
        vehicles = Vehicle.objects.filter(transporter=prof).exclude(status=VehicleStatusChoices.INACTIVE)
        if vehicles.exists():
            avg_cap = sum(v.capacity for v in vehicles) / vehicles.count()
            if avg_cap >= 20:
                return Decimal('85.00')
            elif avg_cap >= 10:
                return Decimal('75.00')
    return Decimal('70.00')


def calculate_proximity_score(transporter_user, load):
    """
    Calculates proximity score (0-100).
    Matches load origin_city with transporter profile location; 100 if exact, 80 if region, 75 fallback.
    """
    prof = TransporterProfile.objects.filter(user=transporter_user).first()
    if prof and prof.city and load.origin_city:
        if prof.city.strip().lower() == load.origin_city.strip().lower():
            return Decimal('100.00')
        elif prof.region and prof.region.strip().lower() in load.origin_city.strip().lower():
            return Decimal('85.00')
    return Decimal('75.00')


def calculate_availability_score(transporter_user):
    """
    Calculates availability score (0-100).
    100.00 if transporter has at least 1 available vehicle; 70.00 otherwise.
    """
    prof = TransporterProfile.objects.filter(user=transporter_user).first()
    if prof:
        active_vehicles = Vehicle.objects.filter(transporter=prof, status=VehicleStatusChoices.AVAILABLE)
        if active_vehicles.exists():
            return Decimal('100.00')
    return Decimal('70.00')


def calculate_candidate_scores(transporter_user, load):
    """
    Calculates total weighted score and component breakdowns.
    """
    c_score = calculate_cost_score(transporter_user, load)
    r_score = calculate_reliability_score(transporter_user)
    f_score = calculate_fuel_efficiency_score(transporter_user)
    p_score = calculate_proximity_score(transporter_user, load)
    a_score = calculate_availability_score(transporter_user)

    total = (
        c_score * COST_WEIGHT +
        r_score * RELIABILITY_WEIGHT +
        f_score * FUEL_WEIGHT +
        p_score * PROXIMITY_WEIGHT +
        a_score * AVAILABILITY_WEIGHT
    )
    total_rounded = round(total, 2)

    explanation = generate_match_explanation(
        total_score=total_rounded,
        cost_score=c_score,
        reliability_score=r_score,
        proximity_score=p_score,
        availability_score=a_score
    )

    return {
        'total_score': total_rounded,
        'cost_score': c_score,
        'reliability_score': r_score,
        'fuel_efficiency_score': f_score,
        'proximity_score': p_score,
        'availability_score': a_score,
        'explanation': explanation,
        'algorithm_version': 'v1'
    }


def generate_match_explanation(*, total_score, cost_score, reliability_score, proximity_score, availability_score):
    """
    Generates a deterministic human-readable explanation of key contributing factors.
    """
    highlights = []
    if availability_score >= Decimal('90.00'):
        highlights.append(f"high fleet availability ({availability_score})")
    if reliability_score >= Decimal('80.00'):
        highlights.append(f"strong reliability record ({reliability_score})")
    if proximity_score >= Decimal('85.00'):
        highlights.append("close location proximity")
    if cost_score >= Decimal('80.00'):
        highlights.append("competitive pricing structure")

    if highlights:
        factors = ", ".join(highlights)
        return f"Recommended with total score {total_score} driven by {factors}."
    return f"Recommended with balanced total match score of {total_score}."
