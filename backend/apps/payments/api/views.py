import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, ValidationException, PermissionDeniedException

from apps.payments.selectors import (
    get_payment_by_id,
    get_payments_for_user,
    get_payouts_for_transporter,
    get_settlements_for_user,
    get_disputes_for_user,
)
from apps.payments.services import (
    create_payment,
    initiate_payment,
    confirm_payment,
    process_provider_webhook,
    process_payout,
    raise_dispute,
    resolve_dispute,
)
from apps.payments.serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    ConfirmPaymentSerializer,
    PayoutSerializer,
    SettlementSerializer,
    PaymentDisputeSerializer,
    RaiseDisputeSerializer,
    ResolveDisputeSerializer,
)
from apps.payments.permissions import (
    CanManagePayments,
    CanRaiseDispute,
    CanResolveDispute,
)

class PaymentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManagePayments]

    def get(self, request):
        payments = get_payments_for_user(request.user)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = serializer.validated_data.get('idempotency_key') or request.headers.get('HTTP_IDEMPOTENCY_KEY') or f"idemp-{uuid.uuid4().hex}"

        payment = create_payment(
            shipment_id=serializer.validated_data['shipment_id'],
            payer_id=request.user.id,
            amount=serializer.validated_data['amount'],
            idempotency_key=idempotency_key,
            currency=serializer.validated_data.get('currency', 'ETB'),
            payment_method=serializer.validated_data.get('payment_method', 'MOBILE_MONEY'),
            provider_name=serializer.validated_data.get('provider', 'MOCK')
        )

        res_serializer = PaymentSerializer(payment)
        return success_response(
            data=res_serializer.data,
            message="Payment created successfully.",
            status_code=status.HTTP_201_CREATED
        )


class PaymentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManagePayments]

    def get(self, request, payment_id):
        payment = get_payment_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment not found.")
        self.check_object_permissions(request, payment)
        serializer = PaymentSerializer(payment)
        return success_response(data=serializer.data)


class PaymentInitiateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManagePayments]

    def post(self, request, payment_id):
        payment = get_payment_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment not found.")
        self.check_object_permissions(request, payment)

        updated_payment = initiate_payment(payment_id=payment.id)
        serializer = PaymentSerializer(updated_payment)
        return success_response(
            data=serializer.data,
            message="Payment initiated with provider gateway."
        )


class PaymentConfirmAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManagePayments]

    def post(self, request, payment_id):
        payment = get_payment_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment not found.")
        self.check_object_permissions(request, payment)

        serializer = ConfirmPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_payment = confirm_payment(
            payment_id=payment.id,
            provider_transaction_id=serializer.validated_data.get('provider_transaction_id')
        )
        res_serializer = PaymentSerializer(updated_payment)
        return success_response(
            data=res_serializer.data,
            message="Payment confirmed and financial reconciliation pipeline executed successfully."
        )


class PaymentWebhookAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        provider_name = request.query_params.get('provider', 'MOCK')
        headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}

        result = process_provider_webhook(
            provider_name=provider_name,
            payload=request.data if isinstance(request.data, dict) else {},
            headers=headers
        )
        return success_response(data=result, message="Webhook event processed.")


class PayoutListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payouts = get_payouts_for_transporter(request.user)
        serializer = PayoutSerializer(payouts, many=True)
        return success_response(data=serializer.data)


class PayoutDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payout_id):
        payouts = get_payouts_for_transporter(request.user)
        payout = next((p for p in payouts if str(p.id) == str(payout_id)), None)
        if not payout:
            raise NotFoundException("Payout not found.")
        serializer = PayoutSerializer(payout)
        return success_response(data=serializer.data)


class ProcessPayoutAPIView(APIView):
    permission_classes = [IsAuthenticated, CanResolveDispute]

    def post(self, request, payout_id):
        payout = process_payout(payout_id=payout_id)
        serializer = PayoutSerializer(payout)
        return success_response(data=serializer.data, message="Payout processed successfully.")


class SettlementListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settlements = get_settlements_for_user(request.user)
        serializer = SettlementSerializer(settlements, many=True)
        return success_response(data=serializer.data)


class SettlementDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, settlement_id):
        settlements = get_settlements_for_user(request.user)
        settlement = next((s for s in settlements if str(s.id) == str(settlement_id)), None)
        if not settlement:
            raise NotFoundException("Settlement not found.")
        serializer = SettlementSerializer(settlement)
        return success_response(data=serializer.data)


class DisputeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanRaiseDispute]

    def get(self, request):
        disputes = get_disputes_for_user(request.user)
        serializer = PaymentDisputeSerializer(disputes, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = RaiseDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dispute = raise_dispute(
            payment_id=serializer.validated_data['payment_id'],
            raised_by_id=request.user.id,
            reason=serializer.validated_data['reason'],
            description=serializer.validated_data['description'],
            disputed_amount=serializer.validated_data.get('disputed_amount')
        )
        res_serializer = PaymentDisputeSerializer(dispute)
        return success_response(
            data=res_serializer.data,
            message="Payment dispute raised successfully.",
            status_code=status.HTTP_201_CREATED
        )


class DisputeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dispute_id):
        disputes = get_disputes_for_user(request.user)
        dispute = next((d for d in disputes if str(d.id) == str(dispute_id)), None)
        if not dispute:
            raise NotFoundException("Payment dispute not found.")
        serializer = PaymentDisputeSerializer(dispute)
        return success_response(data=serializer.data)


class ResolveDisputeAPIView(APIView):
    permission_classes = [IsAuthenticated, CanResolveDispute]

    def post(self, request, dispute_id):
        serializer = ResolveDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dispute = resolve_dispute(
            dispute_id=dispute_id,
            resolved_by_id=request.user.id,
            resolution_status=serializer.validated_data['resolution_status'],
            resolution_notes=serializer.validated_data['resolution_notes']
        )
        res_serializer = PaymentDisputeSerializer(dispute)
        return success_response(data=res_serializer.data, message="Dispute resolved successfully.")
