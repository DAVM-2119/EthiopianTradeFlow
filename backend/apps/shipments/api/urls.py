from django.urls import path
from .views import (
    ShipmentListView,
    ShipmentDetailView,
    ShipmentAssignView,
    ShipmentTransitionView,
    ShipmentCancelView,
    ShipmentEventsListView,
    ProofOfDeliveryView,
    ShipmentCompleteView,
)

urlpatterns = [
    path('', ShipmentListView.as_view(), name='shipment-list'),
    path('<uuid:pk>/', ShipmentDetailView.as_view(), name='shipment-detail'),
    path('<uuid:pk>/assign/', ShipmentAssignView.as_view(), name='shipment-assign'),
    path('<uuid:pk>/transition/', ShipmentTransitionView.as_view(), name='shipment-transition'),
    path('<uuid:pk>/cancel/', ShipmentCancelView.as_view(), name='shipment-cancel'),
    path('<uuid:pk>/events/', ShipmentEventsListView.as_view(), name='shipment-events'),
    path('<uuid:pk>/proof-of-delivery/', ProofOfDeliveryView.as_view(), name='shipment-proof-of-delivery'),
    path('<uuid:pk>/complete/', ShipmentCompleteView.as_view(), name='shipment-complete'),
]
