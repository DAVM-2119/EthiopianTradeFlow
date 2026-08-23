from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.accounts.permissions import IsTransporter
from apps.profiles.services import get_or_create_user_profile, update_user_profile
from apps.profiles.models import DriverProfile, TransporterProfile
from apps.profiles.serializers import DriverProfileSerializer

class UserProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Retrieve current user role-specific profile")
    def get(self, request, *args, **kwargs):
        profile, serializer_class = get_or_create_user_profile(request.user)
        return success_response(data=serializer_class(profile).data)

    @extend_schema(summary="Update current user role-specific profile")
    def patch(self, request, *args, **kwargs):
        updated_data = update_user_profile(request.user, request.data)
        return success_response(data=updated_data, message="Profile updated successfully.")


class TransporterDriverListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTransporter]
    serializer_class = DriverProfileSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return DriverProfile.objects.none()
        transporter_profile, _ = TransporterProfile.objects.get_or_create(user=self.request.user)
        return DriverProfile.objects.filter(transporter=transporter_profile).select_related('user', 'transporter')

    def perform_create(self, serializer):
        transporter_profile, _ = TransporterProfile.objects.get_or_create(user=self.request.user)
        serializer.save(transporter=transporter_profile)
