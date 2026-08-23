from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsTransporter
from apps.fleet.permissions import IsVehicleOwner
from apps.fleet.models import Vehicle
from apps.fleet.serializers import VehicleSerializer
from apps.profiles.models import TransporterProfile
from apps.fleet.services import deactivate_vehicle

class VehicleListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTransporter]
    serializer_class = VehicleSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Vehicle.objects.none()
        if self.request.user.is_staff or getattr(self.request.user, 'role', '') == 'ADMIN':
            return Vehicle.objects.all().select_related('transporter')
        transporter_profile, _ = TransporterProfile.objects.get_or_create(user=self.request.user)
        return Vehicle.objects.filter(transporter=transporter_profile).select_related('transporter')

    def perform_create(self, serializer):
        transporter_profile, _ = TransporterProfile.objects.get_or_create(user=self.request.user)
        serializer.save(transporter=transporter_profile)


class VehicleDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTransporter, IsVehicleOwner]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all().select_related('transporter')

    def perform_destroy(self, instance):
        deactivate_vehicle(instance)
