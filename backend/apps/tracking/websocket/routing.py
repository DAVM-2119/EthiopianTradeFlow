from django.urls import path
from .consumers import TrackingConsumer

websocket_urlpatterns = [
    path('ws/v1/shipments/<uuid:shipment_id>/tracking/', TrackingConsumer.as_asgi(), name='shipment-tracking-ws'),
]
