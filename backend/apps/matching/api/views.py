from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.marketplace.selectors import get_load_by_id
from apps.matching.permissions import IsMatchOwnerOrAdmin
from apps.matching.serializers import MatchRecommendationSerializer, MatchRecommendationDetailSerializer
from apps.matching.services import generate_matches
from apps.matching.selectors import get_active_matches_for_load, get_match_recommendation_by_id

class LoadMatchesListGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Retrieve active freight match recommendations for a load")
    def get(self, request, load_id, *args, **kwargs):
        load = get_load_by_id(load_id)
        if not load:
            raise NotFoundException("Load not found.")

        if load.shipper != request.user and not (request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'):
            raise PermissionDeniedException("Only the load owner or admin can view match recommendations.")

        matches = get_active_matches_for_load(load)
        serializer = MatchRecommendationSerializer(matches, many=True)
        return success_response(
            data=serializer.data,
            message="Match recommendations retrieved successfully."
        )

    @extend_schema(summary="Generate or regenerate freight match recommendations for a load")
    def post(self, request, load_id, *args, **kwargs):
        matches = generate_matches(load_id=load_id, requesting_user=request.user)
        serializer = MatchRecommendationSerializer(matches, many=True)
        return success_response(
            data=serializer.data,
            message="Freight match recommendations generated successfully."
        )


class MatchRecommendationDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsMatchOwnerOrAdmin]
    serializer_class = MatchRecommendationDetailSerializer

    def get_object(self):
        match_id = self.kwargs.get('pk')
        match_rec = get_match_recommendation_by_id(match_id)
        if not match_rec:
            raise NotFoundException("Match recommendation not found.")
        self.check_object_permissions(self.request, match_rec)
        return match_rec

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Match recommendation details retrieved successfully."
        )
