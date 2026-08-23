from django.urls import path
from .views import HealthCheckView, DashboardSummaryAPIView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('dashboard/summary/', DashboardSummaryAPIView.as_view(), name='dashboard-summary'),
]
