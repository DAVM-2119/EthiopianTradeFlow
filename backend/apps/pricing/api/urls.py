from django.urls import path
from .views import (
    LoadPricingDetailAPIView,
    LoadPricingCalculateAPIView,
    LoadPricingHistoryAPIView,
    ContractRateListCreateAPIView
)

urlpatterns = [
    path('loads/<uuid:load_id>/pricing/', LoadPricingDetailAPIView.as_view(), name='load-pricing-detail'),
    path('loads/<uuid:load_id>/pricing/calculate/', LoadPricingCalculateAPIView.as_view(), name='load-pricing-calculate'),
    path('loads/<uuid:load_id>/pricing/history/', LoadPricingHistoryAPIView.as_view(), name='load-pricing-history'),
    path('pricing/contracts/', ContractRateListCreateAPIView.as_view(), name='contract-rate-list-create'),
]
