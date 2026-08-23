from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException, ValidationException
from apps.shipments.models import Shipment
from apps.shipments.permissions import IsShipmentParticipantOrAdmin
from apps.routing.models import Route
from apps.routing.selectors import get_routes_for_shipment, get_route_by_id, get_active_route_for_shipment
from apps.routing.services import calculate_and_save_routes, propose_reroute, confirm_reroute
from apps.routing.serializers import RouteSerializer, RerouteActionSerializer

def verify_shipment_routing_access(user, shipment_id):
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")
    perm = IsShipmentParticipantOrAdmin()
    if not perm.has_object_permission(type('Req', (), {'user': user})(), None, shipment):
        raise PermissionDeniedException("You are not authorized to access routes for this shipment.")
    return shipment


class ShipmentRouteCalculateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shipment_id):
        shipment = verify_shipment_routing_access(request.user, shipment_id)
        route = calculate_and_save_routes(shipment_id=shipment.id)
        serializer = RouteSerializer(route)
        return success_response(
            data=serializer.data,
            message="Candidate routes calculated and best route selected successfully.",
            status_code=status.HTTP_201_CREATED
        )


class ShipmentRouteListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shipment_id):
        shipment = verify_shipment_routing_access(request.user, shipment_id)
        routes = get_routes_for_shipment(shipment.id)
        if not routes.exists():
            active_route = calculate_and_save_routes(shipment_id=shipment.id)
            routes = get_routes_for_shipment(shipment.id)
        serializer = RouteSerializer(routes, many=True)
        return success_response(data=serializer.data)


class RouteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, route_id):
        route = get_route_by_id(route_id)
        if not route:
            raise NotFoundException("Route not found.")
        verify_shipment_routing_access(request.user, route.shipment_id)
        serializer = RouteSerializer(route)
        return success_response(data=serializer.data)


class RouteRerouteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, route_id):
        route = get_route_by_id(route_id)
        if not route:
            raise NotFoundException("Route not found.")
        verify_shipment_routing_access(request.user, route.shipment_id)

        serializer = RerouteActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']

        if action == 'propose':
            risk_score = serializer.validated_data.get('new_risk_score')
            result_route = propose_reroute(route_id=route.id, new_risk_score=risk_score)
            msg = "Reroute proposal created successfully."
        elif action == 'confirm':
            result_route = confirm_reroute(route_id=route.id, accept=True)
            msg = "Reroute proposal confirmed and activated."
        elif action == 'reject':
            result_route = confirm_reroute(route_id=route.id, accept=False)
            msg = "Reroute proposal rejected."

        res_serializer = RouteSerializer(result_route)
        return success_response(data=res_serializer.data, message=msg)
