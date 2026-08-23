import django_filters
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.core.responses import success_response
from apps.accounts.permissions import HasAnyRole
from apps.core.exceptions import NotFoundException
from apps.marketplace.models import Load, LoadStatusChoices, CargoTypeChoices
from apps.marketplace.permissions import IsLoadOwner
from apps.marketplace.serializers import LoadSerializer, LoadCreateSerializer
from apps.marketplace.services import create_load, update_load, post_load, cancel_load

class LoadFilter(django_filters.FilterSet):
    origin_city = django_filters.CharFilter(lookup_expr='icontains')
    destination_city = django_filters.CharFilter(lookup_expr='icontains')
    cargo_type = django_filters.ChoiceFilter(choices=CargoTypeChoices.choices)
    status = django_filters.ChoiceFilter(choices=LoadStatusChoices.choices)
    min_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    max_weight = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    pickup_after = django_filters.DateTimeFilter(field_name='pickup_window_start', lookup_expr='gte')
    pickup_before = django_filters.DateTimeFilter(field_name='pickup_window_start', lookup_expr='lte')

    class Meta:
        model = Load
        fields = ['origin_city', 'destination_city', 'cargo_type', 'status', 'min_weight', 'max_weight', 'pickup_after', 'pickup_before']


class LoadListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filterset_class = LoadFilter
    ordering_fields = ['created_at', 'pickup_window_start', 'weight']
    search_fields = ['title', 'origin_city', 'destination_city', 'special_requirements']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LoadCreateSerializer
        return LoadSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), HasAnyRole(allowed_roles=['SHIPPER', 'FREIGHT_FORWARDER'])]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Load.objects.none()
        my_loads = self.request.query_params.get('my_loads', 'false').lower() == 'true'
        if my_loads and getattr(self.request.user, 'role', '') in ('SHIPPER', 'FREIGHT_FORWARDER'):
            return Load.objects.select_related('shipper').filter(shipper=self.request.user)
        
        if self.request.user.is_staff or getattr(self.request.user, 'role', '') == 'ADMIN':
            return Load.objects.select_related('shipper').all()
        
        return Load.objects.select_related('shipper').filter(status=LoadStatusChoices.POSTED)

    def perform_create(self, serializer):
        load = create_load(self.request.user, serializer.validated_data)
        serializer.instance = load


class LoadDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsLoadOwner]
    serializer_class = LoadSerializer
    queryset = Load.objects.select_related('shipper').all()

    def perform_update(self, serializer):
        updated_load = update_load(self.get_object(), self.request.user, serializer.validated_data)
        serializer.instance = updated_load


class LoadPostView(APIView):
    permission_classes = [IsAuthenticated, IsLoadOwner]
    serializer_class = LoadSerializer

    @extend_schema(summary="Transition load state from DRAFT to POSTED")
    def post(self, request, pk, *args, **kwargs):
        load = Load.objects.filter(id=pk).first()
        if not load:
            raise NotFoundException("Load not found.")
        self.check_object_permissions(request, load)
        posted_load = post_load(load, request.user)
        return success_response(
            data=LoadSerializer(posted_load).data,
            message="Load posted successfully."
        )


class LoadCancelView(APIView):
    permission_classes = [IsAuthenticated, IsLoadOwner]
    serializer_class = LoadSerializer

    @extend_schema(summary="Cancel a load")
    def post(self, request, pk, *args, **kwargs):
        load = Load.objects.filter(id=pk).first()
        if not load:
            raise NotFoundException("Load not found.")
        self.check_object_permissions(request, load)
        cancelled_load = cancel_load(load, request.user)
        return success_response(
            data=LoadSerializer(cancelled_load).data,
            message="Load cancelled successfully."
        )
