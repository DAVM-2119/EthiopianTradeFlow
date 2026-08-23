from django.urls import path
from .views import ShipmentETADetailAPIView, ShipmentETAHistoryAPIView

urlpatterns = [
    path('<uuid:shipment_id>/eta/', ShipmentETADetailAPIView.as_view(), name='shipment-eta-detail'),
    path('<uuid:shipment_id>/eta/history/', ShipmentETAHistoryAPIView.as_view(), name='shipment-eta-history'),
]
