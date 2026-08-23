from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.shipments.permissions import IsShipmentParticipantOrAdmin
from apps.shipments.models import Shipment
from apps.shipments.serializers import (
    ShipmentListSerializer,
    ShipmentDetailSerializer,
    ShipmentAssignmentSerializer,
    ShipmentTransitionSerializer,
    ShipmentCancellationSerializer,
    ShipmentEventSerializer,
    ProofOfDeliverySerializer,
)
from apps.shipments.services import (
    assign_shipment_resources,
    transition_shipment,
    cancel_shipment,
    record_proof_of_delivery,
    complete_shipment,
)
from apps.shipments.selectors import (
    get_shipment_by_id,
    get_user_shipments,
    get_shipment_events,
    get_proof_of_delivery,
)

class ShipmentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShipmentListSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Shipment.objects.none()
        status_filter = self.request.query_params.get('status')
        return get_user_shipments(self.request.user, status_filter=status_filter)


class ShipmentDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentDetailSerializer

    def get_object(self):
        shipment_id = self.kwargs.get('pk')
        shipment = get_shipment_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(self.request, shipment)
        return shipment


class ShipmentAssignView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentAssignmentSerializer

    @extend_schema(summary="Assign vehicle and driver to shipment")
    def post(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        serializer = ShipmentAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assigned_shipment = assign_shipment_resources(
            shipment=shipment,
            actor=request.user,
            vehicle_id=serializer.validated_data['vehicle_id'],
            driver_id=serializer.validated_data['driver_id']
        )
        return success_response(
            data=ShipmentDetailSerializer(assigned_shipment).data,
            message="Shipment resources assigned successfully."
        )


class ShipmentTransitionView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentTransitionSerializer

    @extend_schema(summary="Transition shipment state")
    def post(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        serializer = ShipmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_shipment = transition_shipment(
            shipment=shipment,
            target_status=serializer.validated_data['status'],
            actor=request.user,
            description=serializer.validated_data.get('description', '')
        )
        return success_response(
            data=ShipmentDetailSerializer(updated_shipment).data,
            message=f"Shipment status updated to {updated_shipment.status} successfully."
        )


class ShipmentCancelView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentCancellationSerializer

    @extend_schema(summary="Cancel a shipment")
    def post(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        serializer = ShipmentCancellationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancelled = cancel_shipment(
            shipment=shipment,
            actor=request.user,
            reason=serializer.validated_data['reason']
        )
        return success_response(
            data=ShipmentDetailSerializer(cancelled).data,
            message="Shipment cancelled successfully."
        )


class ShipmentEventsListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentEventSerializer

    def get_queryset(self):
        shipment_id = self.kwargs.get('pk')
        shipment = get_shipment_by_id(shipment_id)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(self.request, shipment)
        return get_shipment_events(shipment)


class ProofOfDeliveryView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ProofOfDeliverySerializer

    @extend_schema(summary="Retrieve proof of delivery for shipment")
    def get(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        pod = get_proof_of_delivery(shipment)
        if not pod:
            raise NotFoundException("Proof of delivery has not been submitted for this shipment.")

        return success_response(
            data=ProofOfDeliverySerializer(pod).data,
            message="Proof of delivery retrieved successfully."
        )

    @extend_schema(summary="Submit proof of delivery for shipment")
    def post(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        serializer = ProofOfDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pod = record_proof_of_delivery(
            shipment=shipment,
            actor=request.user,
            receiver_name=serializer.validated_data['receiver_name'],
            delivery_timestamp=serializer.validated_data['delivery_timestamp'],
            signature_reference=serializer.validated_data.get('signature_reference', ''),
            photo_reference=serializer.validated_data.get('photo_reference', ''),
            notes=serializer.validated_data.get('notes', '')
        )
        return success_response(
            data=ProofOfDeliverySerializer(pod).data,
            message="Proof of delivery recorded successfully."
        )


class ShipmentCompleteView(APIView):
    permission_classes = [IsAuthenticated, IsShipmentParticipantOrAdmin]
    serializer_class = ShipmentDetailSerializer

    @extend_schema(summary="Complete shipment upon verified proof of delivery")
    def post(self, request, pk, *args, **kwargs):
        shipment = get_shipment_by_id(pk)
        if not shipment:
            raise NotFoundException("Shipment not found.")
        self.check_object_permissions(request, shipment)

        completed = complete_shipment(shipment=shipment, actor=request.user)
        return success_response(
            data=ShipmentDetailSerializer(completed).data,
            message="Shipment completed successfully."
        )
