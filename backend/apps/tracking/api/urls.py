from django.urls import path
from .views import (
    TrackingEventIngestView,
    ShipmentTrackingHistoryView,
    ShipmentLatestTrackingView,
)

urlpatterns = [
    path('events/', TrackingEventIngestView.as_view(), name='tracking-event-ingest'),
    path('shipments/<uuid:shipment_id>/tracking/', ShipmentTrackingHistoryView.as_view(), name='shipment-tracking-history'),
    path('shipments/<uuid:shipment_id>/tracking/latest/', ShipmentLatestTrackingView.as_view(), name='shipment-tracking-latest'),
]
