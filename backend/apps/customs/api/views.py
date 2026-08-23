from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.shipments.models import Shipment
from apps.customs.models import CustomsDocument
from apps.customs.selectors import get_customs_documents_for_shipment, get_customs_document_by_id
from apps.customs.services import (
    upload_customs_document,
    validate_shipment_customs_documents,
    submit_customs_clearance,
    update_customs_clearance_status,
)
from apps.customs.serializers import (
    CustomsDocumentSerializer,
    CustomsDocumentUploadSerializer,
    CustomsValidationResultSerializer,
    CustomsStatusUpdateSerializer,
)
from apps.customs.permissions import CanViewCustomsDocument, CanUploadCustomsDocument, CanReviewCustomsClearance

def verify_shipment_customs_access(user, shipment_id):
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role in ('ADMIN', 'CUSTOMS_STAFF', 'FREIGHT_FORWARDER'):
        return shipment
    if shipment.shipper == user or shipment.transporter == user or shipment.driver == user:
        return shipment
    raise PermissionDeniedException("You are not authorized to access customs documents for this shipment.")


class ShipmentCustomsDocumentListUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, CanUploadCustomsDocument]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, shipment_id):
        shipment = verify_shipment_customs_access(request.user, shipment_id)
        docs = get_customs_documents_for_shipment(shipment.id)
        serializer = CustomsDocumentSerializer(docs, many=True)
        return success_response(data=serializer.data)

    def post(self, request, shipment_id):
        shipment = verify_shipment_customs_access(request.user, shipment_id)
        serializer = CustomsDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doc = upload_customs_document(
            shipment_id=shipment.id,
            user=request.user,
            document_type=serializer.validated_data['document_type'],
            file_obj=serializer.validated_data['file'],
            document_number=serializer.validated_data.get('document_number', ''),
            issue_date=serializer.validated_data.get('issue_date'),
            declared_value=serializer.validated_data.get('declared_value'),
            quantity=serializer.validated_data.get('quantity')
        )
        res_serializer = CustomsDocumentSerializer(doc)
        return success_response(
            data=res_serializer.data,
            message="Customs document uploaded successfully.",
            status_code=status.HTTP_201_CREATED
        )


class CustomsDocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewCustomsDocument]

    def get(self, request, document_id):
        doc = get_customs_document_by_id(document_id)
        if not doc:
            raise NotFoundException("Customs document not found.")
        self.check_object_permissions(request, doc)
        serializer = CustomsDocumentSerializer(doc)
        return success_response(data=serializer.data)


class ShipmentCustomsValidateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shipment_id):
        shipment = verify_shipment_customs_access(request.user, shipment_id)
        result = validate_shipment_customs_documents(shipment_id=shipment.id)
        serializer = CustomsValidationResultSerializer(result)
        return success_response(
            data=serializer.data,
            message="Customs document validation completed."
        )


class ShipmentCustomsSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shipment_id):
        shipment = verify_shipment_customs_access(request.user, shipment_id)
        result = submit_customs_clearance(shipment_id=shipment.id, user=request.user)
        return success_response(
            data=result,
            message="Customs clearance submitted successfully."
        )


class ShipmentCustomsStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, CanReviewCustomsClearance]

    def post(self, request, shipment_id):
        shipment = Shipment.objects.filter(id=shipment_id).first()
        if not shipment:
            raise NotFoundException("Shipment not found.")

        serializer = CustomsStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = update_customs_clearance_status(
            shipment_id=shipment.id,
            reviewer_user=request.user,
            new_status=serializer.validated_data['status'],
            rejection_reason=serializer.validated_data.get('rejection_reason', '')
        )
        return success_response(
            data=result,
            message=f"Customs clearance status updated to {serializer.validated_data['status']}."
        )
