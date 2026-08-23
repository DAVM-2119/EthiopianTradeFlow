from django.utils import timezone
from django.db import transaction
from django.conf import settings
from apps.accounts.models import User, RoleChoices
from apps.marketplace.models import Load, LoadStatusChoices
from apps.verification.services import is_marketplace_eligible
from apps.matching.models import MatchRecommendation
from apps.matching.services.scoring_service import calculate_candidate_scores
from apps.core.exceptions import NotFoundException, ConflictException, PermissionDeniedException

def generate_matches(*, load_id, requesting_user, shortlist_size=None):
    """
    Generates deterministic candidate recommendations for a load.
    1. Validates load state == POSTED.
    2. Enforces load ownership / admin authorization.
    3. Finds eligible candidate transporters (verified, non-suspended, non-owner).
    4. Calculates candidate scores & sorts deterministically.
    5. Atomically deactivates previous active recommendations and creates new top-N shortlist.
    """
    load = Load.objects.select_related('shipper').filter(id=load_id).first()
    if not load:
        raise NotFoundException("Load not found.")

    if load.shipper != requesting_user and not (requesting_user.is_staff or getattr(requesting_user, 'role', '') == 'ADMIN'):
        raise PermissionDeniedException("Only the owner of the load or an admin can generate match recommendations.")

    if load.status != LoadStatusChoices.POSTED:
        raise ConflictException("Match recommendations can only be generated for POSTED loads.")

    if shortlist_size is None:
        shortlist_size = getattr(settings, 'DEFAULT_MATCH_SHORTLIST_SIZE', 10)

    candidate_users = User.objects.filter(
        role__in=[RoleChoices.TRANSPORTER, RoleChoices.FREIGHT_FORWARDER],
        is_active=True
    ).exclude(id=load.shipper_id)

    scored_candidates = []
    for transporter in candidate_users:
        if is_marketplace_eligible(transporter):
            scores = calculate_candidate_scores(transporter, load)
            scored_candidates.append({
                'transporter': transporter,
                'scores': scores
            })

    scored_candidates.sort(
        key=lambda item: (
            item['scores']['total_score'],
            item['scores']['reliability_score'],
            item['scores']['availability_score'],
            str(item['transporter'].id)
        ),
        reverse=True
    )

    top_candidates = scored_candidates[:shortlist_size]
    now = timezone.now()

    new_recommendations = []
    with transaction.atomic():
        MatchRecommendation.objects.filter(load=load, is_active=True).update(is_active=False)

        for index, item in enumerate(top_candidates, start=1):
            s = item['scores']
            rec = MatchRecommendation(
                load=load,
                transporter=item['transporter'],
                rank=index,
                total_score=s['total_score'],
                cost_score=s['cost_score'],
                reliability_score=s['reliability_score'],
                fuel_efficiency_score=s['fuel_efficiency_score'],
                proximity_score=s['proximity_score'],
                availability_score=s['availability_score'],
                explanation=s['explanation'],
                algorithm_version=s['algorithm_version'],
                generated_at=now,
                is_active=True
            )
            new_recommendations.append(rec)

        if new_recommendations:
            MatchRecommendation.objects.bulk_create(new_recommendations)

    return MatchRecommendation.objects.select_related('transporter').filter(load=load, is_active=True).order_by('rank')
