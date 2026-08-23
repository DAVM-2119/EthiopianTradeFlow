from django.urls import path
from .views import LoadMatchesListGenerateView, MatchRecommendationDetailView

urlpatterns = [
    path('loads/<uuid:load_id>/matches/', LoadMatchesListGenerateView.as_view(), name='load-matches-list-generate'),
    path('matches/<uuid:pk>/', MatchRecommendationDetailView.as_view(), name='match-recommendation-detail'),
]
