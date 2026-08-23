from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.shipments.models import Shipment
from apps.fleet.models import Vehicle
from apps.accounts.models import User
from apps.analytics.selectors import (
    get_fuel_record_for_shipment,
    get_vehicle_fuel_summary,
    get_driver_fuel_summary,
    get_fuel_trends_data,
    get_transporter_performance,
    get_transporter_performance_history,
    get_corridor_benchmark_data
)
from apps.analytics.services import (
    record_trip_fuel,
    generate_fuel_recommendations,
    generate_monthly_performance
)
from apps.analytics.serializers import (
    TripFuelRecordSerializer,
    RecordTripFuelSerializer,
    VehicleFuelMetricsSerializer,
    DriverFuelMetricsSerializer,
    FuelTrendSerializer,
    FuelRecommendationSerializer,
    TransporterPerformanceSerializer,
    CorridorBenchmarkSerializer,
    TransporterDashboardResponseSerializer
)
from apps.analytics.permissions import (
    CanViewFuelAnalytics,
    CanRecordFuelData,
    CanViewTransporterPerformance
)

def verify_shipment_analytics_access(user, shipment_id):
    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")
    user_role = getattr(user, 'role', '')
    if user.is_staff or user_role == 'ADMIN':
        return shipment
    if shipment.shipper == user or shipment.transporter == user or shipment.driver == user:
        return shipment
    raise PermissionDeniedException("You are not authorized to access fuel analytics for this shipment.")


class ShipmentFuelAPIView(APIView):
    permission_classes = [IsAuthenticated, CanRecordFuelData]

    def get(self, request, shipment_id):
        shipment = verify_shipment_analytics_access(request.user, shipment_id)
        record = get_fuel_record_for_shipment(shipment.id)
        if not record:
            record = record_trip_fuel(shipment_id=shipment.id)
        serializer = TripFuelRecordSerializer(record)
        return success_response(data=serializer.data)

    def post(self, request, shipment_id):
        shipment = verify_shipment_analytics_access(request.user, shipment_id)
        serializer = RecordTripFuelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = record_trip_fuel(
            shipment_id=shipment.id,
            actual_fuel_liters=serializer.validated_data.get('actual_fuel_liters'),
            distance_km=serializer.validated_data.get('distance_km'),
            estimated_fuel_liters=serializer.validated_data.get('estimated_fuel_liters'),
            data_source=serializer.validated_data.get('data_source', 'MANUAL'),
            notes=serializer.validated_data.get('notes', '')
        )
        res_serializer = TripFuelRecordSerializer(record)
        return success_response(
            data=res_serializer.data,
            message="Trip fuel consumption record updated successfully.",
            status_code=status.HTTP_200_OK
        )


class VehicleFuelMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewFuelAnalytics]

    def get(self, request, vehicle_id):
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()
        if not vehicle:
            raise NotFoundException("Vehicle not found.")

        user_role = getattr(request.user, 'role', '')
        if not (request.user.is_staff or user_role == 'ADMIN' or vehicle.transporter.user == request.user):
            raise PermissionDeniedException("You are not authorized to view fuel metrics for this vehicle.")

        summary = get_vehicle_fuel_summary(vehicle.id)
        serializer = VehicleFuelMetricsSerializer(summary)
        return success_response(data=serializer.data)


class DriverFuelMetricsAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewFuelAnalytics]

    def get(self, request, driver_id):
        driver = User.objects.filter(id=driver_id).first()
        if not driver:
            raise NotFoundException("Driver not found.")

        user_role = getattr(request.user, 'role', '')
        if not (request.user.is_staff or user_role == 'ADMIN' or driver == request.user or user_role == 'TRANSPORTER'):
            raise PermissionDeniedException("You are not authorized to view fuel metrics for this driver.")

        summary = get_driver_fuel_summary(driver.id)
        serializer = DriverFuelMetricsSerializer(summary)
        return success_response(data=serializer.data)


class FuelTrendsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        driver_id = request.query_params.get('driver_id')
        period = request.query_params.get('period', 'monthly')

        trends = get_fuel_trends_data(vehicle_id=vehicle_id, driver_id=driver_id, period=period)
        serializer = FuelTrendSerializer(trends, many=True)
        return success_response(data=serializer.data)


class FuelRecommendationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vehicle_id = request.query_params.get('vehicle_id')
        driver_id = request.query_params.get('driver_id')

        recs = generate_fuel_recommendations(vehicle_id=vehicle_id, driver_id=driver_id)
        serializer = FuelRecommendationSerializer(recs, many=True)
        return success_response(data=serializer.data)


class TransporterPerformanceDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewTransporterPerformance]

    def get(self, request):
        now = timezone.now()
        year = int(request.query_params.get('year', now.year))
        month = int(request.query_params.get('month', now.month))

        target_transporter_id = request.user.id
        param_transporter_id = request.query_params.get('transporter_id')
        user_role = getattr(request.user, 'role', '')

        if param_transporter_id:
            if not (request.user.is_staff or user_role == 'ADMIN'):
                raise PermissionDeniedException("You are not authorized to view performance metrics for other transporters.")
            target_transporter_id = param_transporter_id

        perf = generate_monthly_performance(transporter_id=target_transporter_id, year=year, month=month)
        benchmark = get_corridor_benchmark_data(year=year, month=month)

        perf_serializer = TransporterPerformanceSerializer(perf)
        bench_serializer = CorridorBenchmarkSerializer(benchmark)

        return success_response(data={
            "performance": perf_serializer.data,
            "corridor_benchmark": bench_serializer.data
        })


class TransporterPerformanceHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewTransporterPerformance]

    def get(self, request):
        target_transporter_id = request.user.id
        param_transporter_id = request.query_params.get('transporter_id')
        user_role = getattr(request.user, 'role', '')

        if param_transporter_id:
            if not (request.user.is_staff or user_role == 'ADMIN'):
                raise PermissionDeniedException("You are not authorized to view performance metrics for other transporters.")
            target_transporter_id = param_transporter_id

        history = get_transporter_performance_history(target_transporter_id)
        serializer = TransporterPerformanceSerializer(history, many=True)
        return success_response(data=serializer.data)
