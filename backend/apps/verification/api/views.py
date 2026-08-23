from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.accounts.permissions import IsAdmin
from apps.core.exceptions import NotFoundException
from apps.verification.models import Verification, VerificationHistory
from apps.verification.serializers import (
    VerificationSerializer,
    AdminVerificationDetailSerializer,
    VerificationActionSerializer,
    VerificationHistorySerializer,
)
from apps.verification.services import (
    submit_verification,
    approve_verification,
    suspend_verification,
    reject_verification,
)
from apps.verification.selectors import (
    get_user_verification,
    get_verification_detail,
    get_verification_history,
)

class UserVerificationMeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerificationSerializer

    @extend_schema(summary="Retrieve current authenticated user verification status")
    def get(self, request, *args, **kwargs):
        verification = get_user_verification(request.user)
        if not verification:
            return success_response(
                data={"status": "NOT_SUBMITTED", "submitted_at": None, "verified_at": None},
                message="No verification record submitted yet."
            )
        return success_response(data=VerificationSerializer(verification).data)


class UserVerificationSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerificationSerializer

    @extend_schema(summary="Submit user profile/fleet for verification review")
    def post(self, request, *args, **kwargs):
        verification = submit_verification(request.user)
        return success_response(
            data=VerificationSerializer(verification).data,
            message="Verification submitted successfully and is under review.",
            status_code=status.HTTP_201_CREATED
        )


class AdminVerificationQueueView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = VerificationSerializer
    filterset_fields = ['status']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['submitted_at', 'created_at']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Verification.objects.none()
        return Verification.objects.select_related('user').all().order_by('-submitted_at')


class AdminVerificationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminVerificationDetailSerializer

    @extend_schema(summary="Admin inspect detailed verification payload")
    def get(self, request, pk, *args, **kwargs):
        verification = get_verification_detail(pk)
        if not verification:
            raise NotFoundException("Verification record not found.")
        return success_response(data=AdminVerificationDetailSerializer(verification).data)


class AdminVerificationApproveView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = VerificationActionSerializer

    @extend_schema(request=VerificationActionSerializer, summary="Admin approve user verification")
    def post(self, request, pk, *args, **kwargs):
        serializer = VerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        verification = approve_verification(
            admin_user=request.user,
            verification_id=pk,
            reason=data.get('reason') or "Approved by administrator",
            notes=data.get('notes', '')
        )
        return success_response(
            data=VerificationSerializer(verification).data,
            message="Verification approved successfully."
        )


class AdminVerificationSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = VerificationActionSerializer

    @extend_schema(request=VerificationActionSerializer, summary="Admin suspend user verification")
    def post(self, request, pk, *args, **kwargs):
        serializer = VerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        verification = suspend_verification(
            admin_user=request.user,
            verification_id=pk,
            reason=data.get('reason'),
            notes=data.get('notes', '')
        )
        return success_response(
            data=VerificationSerializer(verification).data,
            message="Verification suspended successfully."
        )


class AdminVerificationRejectView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = VerificationActionSerializer

    @extend_schema(request=VerificationActionSerializer, summary="Admin reject user verification")
    def post(self, request, pk, *args, **kwargs):
        serializer = VerificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        verification = reject_verification(
            admin_user=request.user,
            verification_id=pk,
            reason=data.get('reason'),
            notes=data.get('notes', '')
        )
        return success_response(
            data=VerificationSerializer(verification).data,
            message="Verification rejected successfully."
        )


class AdminVerificationHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = VerificationHistorySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return VerificationHistory.objects.none()
        pk = self.kwargs.get('pk')
        return get_verification_history(pk)
