from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.shipments.models import Shipment
from apps.shipments.permissions import IsShipmentParticipantOrAdmin
from apps.eta.selectors import get_latest_eta_prediction, get_eta_prediction_history
from apps.eta.services import calculate_and_save_eta
from apps.eta.serializers import ETAPredictionSerializer

def verify_shipment_access(user, shipment_id):
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")
    perm = IsShipmentParticipantOrAdmin()
    if not perm.has_object_permission(type('Req', (), {'user': user})(), None, shipment):
        raise PermissionDeniedException("You are not authorized to view ETA predictions for this shipment.")
    return shipment


class ShipmentETADetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shipment_id):
        shipment = verify_shipment_access(request.user, shipment_id)
        
        eta = get_latest_eta_prediction(shipment.id)
        if not eta:
            eta = calculate_and_save_eta(shipment_id=shipment.id)

        serializer = ETAPredictionSerializer(eta)
        return success_response(data=serializer.data)


class ShipmentETAHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shipment_id):
        shipment = verify_shipment_access(request.user, shipment_id)
        history = get_eta_prediction_history(shipment.id)
        serializer = ETAPredictionSerializer(history, many=True)
        return success_response(data=serializer.data)
