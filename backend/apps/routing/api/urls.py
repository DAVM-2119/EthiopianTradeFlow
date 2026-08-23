from django.urls import path
from .views import (
    ShipmentRouteCalculateAPIView,
    ShipmentRouteListAPIView,
    RouteDetailAPIView,
    RouteRerouteAPIView
)

urlpatterns = [
    path('shipments/<uuid:shipment_id>/routes/calculate/', ShipmentRouteCalculateAPIView.as_view(), name='shipment-route-calculate'),
    path('shipments/<uuid:shipment_id>/routes/', ShipmentRouteListAPIView.as_view(), name='shipment-route-list'),
    path('routes/<uuid:route_id>/', RouteDetailAPIView.as_view(), name='route-detail'),
    path('routes/<uuid:route_id>/reroute/', RouteRerouteAPIView.as_view(), name='route-reroute'),
]
