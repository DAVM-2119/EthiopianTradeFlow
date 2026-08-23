from django.urls import path
from .views import (
    RiskZoneListCreateAPIView,
    RiskZoneDetailAPIView,
    IncidentListCreateAPIView,
    IncidentVerifyAPIView,
    SecurityAlertListAPIView,
    SecurityAlertDetailAPIView,
    SecurityAlertAcknowledgeAPIView,
    CheckLocationRiskAPIView,
)

urlpatterns = [
    path('risk-zones/', RiskZoneListCreateAPIView.as_view(), name='risk-zone-list-create'),
    path('risk-zones/<uuid:zone_id>/', RiskZoneDetailAPIView.as_view(), name='risk-zone-detail'),
    path('incidents/', IncidentListCreateAPIView.as_view(), name='incident-list-create'),
    path('incidents/<uuid:incident_id>/verify/', IncidentVerifyAPIView.as_view(), name='incident-verify'),
    path('security-alerts/', SecurityAlertListAPIView.as_view(), name='security-alert-list'),
    path('security-alerts/<uuid:alert_id>/', SecurityAlertDetailAPIView.as_view(), name='security-alert-detail'),
    path('security-alerts/<uuid:alert_id>/acknowledge/', SecurityAlertAcknowledgeAPIView.as_view(), name='security-alert-acknowledge'),
    path('risk/check-location/', CheckLocationRiskAPIView.as_view(), name='risk-check-location'),
]
