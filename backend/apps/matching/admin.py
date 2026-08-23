from django.contrib import admin
from apps.matching.models import MatchRecommendation

@admin.register(MatchRecommendation)
class MatchRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'load', 'transporter', 'rank', 'total_score', 'algorithm_version', 'is_active', 'generated_at')
    list_filter = ('is_active', 'algorithm_version', 'generated_at')
    search_fields = ('load__title', 'transporter__email', 'explanation')
    readonly_fields = (
        'load', 'transporter', 'rank', 'total_score', 'cost_score',
        'reliability_score', 'fuel_efficiency_score', 'proximity_score',
        'availability_score', 'explanation', 'algorithm_version',
        'generated_at', 'is_active', 'created_at', 'updated_at'
    )

    def has_add_permission(self, request):
        return False
