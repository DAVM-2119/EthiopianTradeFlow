from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.shipments.selectors import get_shipment_by_id
from apps.shipments.permissions import IsShipmentParticipantOrAdmin
from apps.tracking.permissions import IsShipmentDriverOrParticipant
from apps.tracking.serializers import (
    TrackingEventIngestSerializer,
    TrackingEventSerializer,
)
from apps.tracking.services import record_tracking_event
from apps.tracking.selectors import (
    get_shipment_tracking_events,
    get_latest_tracking_event,
)

class TrackingEventIngestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackingEventIngestSerializer

    @extend_schema(summary="Ingest GPS tracking event for a shipment")
    def post(self, request, *args, **kwargs):
        serializer = TrackingEventIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        tracking_event = record_tracking_event(
            shipment_id=data['shipment'],
            driver_user=request.user,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data.get('speed'),
            heading=data.get('heading'),
            recorded_at=data['recorded_at'],
            event_id=data.get('event_id')
        )

        return success_response(
            data=TrackingEventSerializer(tracking_event).data,
            message="GPS tracking event recorded successfully.",
            status_code=status.HTTP_201_CREATED
        )


class ShipmentTrackingHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = TrackingEventSerializer

    def get_queryset(self):
        shipment_id = self.kwargs.get('shipment_id')
        shipment = get_shipment_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(self.request, shipment)

        limit_param = self.request.query_params.get('limit', 100)
        try:
            limit = int(limit_param)
        except ValueError:
            limit = 100

        return get_shipment_tracking_events(shipment_id, limit=limit)


class ShipmentLatestTrackingView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = TrackingEventSerializer

    @extend_schema(summary="Retrieve latest GPS position update for shipment")
    def get(self, request, shipment_id, *args, **kwargs):
        shipment = get_shipment_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        latest_event = get_latest_tracking_event(shipment_id)
        if not latest_event:
            raise NotFoundException("No GPS tracking events recorded for this shipment.")

        return success_response(
            data=TrackingEventSerializer(latest_event).data,
            message="Latest tracking event retrieved successfully."
        )
