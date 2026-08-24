from django.urls import path
from .views import (
    ShipmentFuelAPIView,
    VehicleFuelMetricsAPIView,
    DriverFuelMetricsAPIView,
    FuelTrendsAPIView,
    FuelRecommendationsAPIView,
    TransporterPerformanceDashboardAPIView,
    TransporterPerformanceHistoryAPIView,
)
from .ml_views import MLModelListView, MLETAPredictView

urlpatterns = [
    path('shipments/<uuid:shipment_id>/fuel/', ShipmentFuelAPIView.as_view(), name='shipment-fuel'),
    path('vehicles/<uuid:vehicle_id>/fuel-metrics/', VehicleFuelMetricsAPIView.as_view(), name='vehicle-fuel-metrics'),
    path('drivers/<uuid:driver_id>/fuel-metrics/', DriverFuelMetricsAPIView.as_view(), name='driver-fuel-metrics'),
    path('analytics/fuel/trends/', FuelTrendsAPIView.as_view(), name='analytics-fuel-trends'),
    path('analytics/fuel/recommendations/', FuelRecommendationsAPIView.as_view(), name='analytics-fuel-recommendations'),
    path('analytics/transporter/performance/', TransporterPerformanceDashboardAPIView.as_view(), name='transporter-performance-dashboard'),
    path('analytics/transporter/performance/history/', TransporterPerformanceHistoryAPIView.as_view(), name='transporter-performance-history'),
    path('ml/models/', MLModelListView.as_view(), name='ml-models-list'),
    path('ml/eta/predict/', MLETAPredictView.as_view(), name='ml-eta-predict'),
]
