from rest_framework import serializers
from apps.matching.models import MatchRecommendation
from apps.accounts.serializers import UserSerializer

class MatchRecommendationSerializer(serializers.ModelSerializer):
    transporter_email = serializers.CharField(source='transporter.email', read_only=True)
    transporter_id = serializers.UUIDField(source='transporter.id', read_only=True)
    load_id = serializers.UUIDField(source='load.id', read_only=True)

    scores = serializers.SerializerMethodField()

    class Meta:
        model = MatchRecommendation
        fields = (
            'id', 'load_id', 'transporter_id', 'transporter_email', 'rank',
            'total_score', 'scores', 'explanation', 'algorithm_version',
            'generated_at', 'is_active'
        )
        read_only_fields = fields

    def get_scores(self, obj):
        return {
            'cost': float(obj.cost_score),
            'reliability': float(obj.reliability_score),
            'fuel_efficiency': float(obj.fuel_efficiency_score),
            'proximity': float(obj.proximity_score),
            'availability': float(obj.availability_score),
        }


class MatchRecommendationDetailSerializer(MatchRecommendationSerializer):
    transporter = UserSerializer(read_only=True)

    class Meta(MatchRecommendationSerializer.Meta):
        fields = (
            'id', 'load_id', 'transporter', 'rank', 'total_score',
            'cost_score', 'reliability_score', 'fuel_efficiency_score',
            'proximity_score', 'availability_score', 'scores', 'explanation',
            'algorithm_version', 'generated_at', 'is_active', 'created_at'
        )
        read_only_fields = fields
