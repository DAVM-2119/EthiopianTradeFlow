from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException, ValidationException
from apps.risk.models import RiskZone, IncidentReport, SecurityAlert
from apps.risk.selectors import (
    get_active_risk_zones,
    get_security_alerts_for_user,
    get_security_alerts_for_shipment,
    get_incidents_for_shipment,
    get_active_incidents
)
from apps.risk.services import (
    create_risk_zone,
    update_risk_zone,
    report_incident,
    verify_incident,
    acknowledge_alert,
    check_location_for_risk
)
from apps.risk.serializers import (
    RiskZoneSerializer,
    CreateRiskZoneSerializer,
    IncidentReportSerializer,
    ReportIncidentSerializer,
    VerifyIncidentSerializer,
    SecurityAlertSerializer,
    CheckLocationRequestSerializer,
    CheckLocationResponseSerializer
)
from apps.risk.permissions import (
    CanManageRiskZones,
    CanReportIncident,
    CanViewSecurityAlerts
)


class RiskZoneListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageRiskZones]

    def get(self, request):
        zones = get_active_risk_zones()
        serializer = RiskZoneSerializer(zones, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = CreateRiskZoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        zone = create_risk_zone(
            name=serializer.validated_data['name'],
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            radius_km=serializer.validated_data.get('radius_km', 10.0),
            severity=serializer.validated_data.get('severity', 'HIGH'),
            source=serializer.validated_data.get('source', 'ADMIN'),
            description=serializer.validated_data.get('description', ''),
            effective_from=serializer.validated_data.get('effective_from'),
            effective_until=serializer.validated_data.get('effective_until'),
            created_by=request.user
        )
        res_serializer = RiskZoneSerializer(zone)
        return success_response(
            data=res_serializer.data,
            message="RiskZone created successfully.",
            status_code=status.HTTP_201_CREATED
        )


class RiskZoneDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageRiskZones]

    def get(self, request, zone_id):
        zone = RiskZone.objects.filter(id=zone_id).first()
        if not zone:
            raise NotFoundException("RiskZone not found.")
        serializer = RiskZoneSerializer(zone)
        return success_response(data=serializer.data)

    def patch(self, request, zone_id):
        zone = update_risk_zone(zone_id, **request.data)
        serializer = RiskZoneSerializer(zone)
        return success_response(data=serializer.data, message="RiskZone updated successfully.")

    def delete(self, request, zone_id):
        zone = RiskZone.objects.filter(id=zone_id).first()
        if not zone:
            raise NotFoundException("RiskZone not found.")
        zone.is_active = False
        zone.save()
        return success_response(message="RiskZone deactivated successfully.")


class IncidentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, CanReportIncident]

    def get(self, request):
        shipment_id = request.query_params.get('shipment_id')
        if shipment_id:
            incidents = get_incidents_for_shipment(shipment_id)
        else:
            incidents = get_active_incidents()
        serializer = IncidentReportSerializer(incidents, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = ReportIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        incident = report_incident(
            reported_by=request.user,
            incident_type=serializer.validated_data['incident_type'],
            description=serializer.validated_data['description'],
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            shipment_id=serializer.validated_data.get('shipment_id'),
            severity=serializer.validated_data.get('severity', 'MEDIUM')
        )
        res_serializer = IncidentReportSerializer(incident)
        return success_response(
            data=res_serializer.data,
            message="Incident reported successfully.",
            status_code=status.HTTP_201_CREATED
        )


class IncidentVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageRiskZones]

    def post(self, request, incident_id):
        serializer = VerifyIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        incident = verify_incident(
            incident_id=incident_id,
            verified_by=request.user,
            notes=serializer.validated_data.get('verification_notes', ''),
            status=serializer.validated_data['status']
        )
        res_serializer = IncidentReportSerializer(incident)
        return success_response(data=res_serializer.data, message="Incident status updated.")


class SecurityAlertListAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewSecurityAlerts]

    def get(self, request):
        shipment_id = request.query_params.get('shipment_id')
        active_only = request.query_params.get('active_only', 'false').lower() == 'true'

        if shipment_id:
            alerts = get_security_alerts_for_shipment(shipment_id, active_only=active_only)
        else:
            alerts = get_security_alerts_for_user(request.user, active_only=active_only)

        serializer = SecurityAlertSerializer(alerts, many=True)
        return success_response(data=serializer.data)


class SecurityAlertDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewSecurityAlerts]

    def get(self, request, alert_id):
        alert = SecurityAlert.objects.filter(id=alert_id).first()
        if not alert:
            raise NotFoundException("SecurityAlert not found.")
        self.check_object_permissions(request, alert)
        serializer = SecurityAlertSerializer(alert)
        return success_response(data=serializer.data)


class SecurityAlertAcknowledgeAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewSecurityAlerts]

    def post(self, request, alert_id):
        alert = SecurityAlert.objects.filter(id=alert_id).first()
        if not alert:
            raise NotFoundException("SecurityAlert not found.")
        self.check_object_permissions(request, alert)

        updated_alert = acknowledge_alert(alert.id, user=request.user)
        serializer = SecurityAlertSerializer(updated_alert)
        return success_response(data=serializer.data, message="Security alert acknowledged.")


class CheckLocationRiskAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckLocationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_location_for_risk(
            shipment_id=serializer.validated_data['shipment_id'],
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            driver_id=request.user.id
        )

        res_serializer = CheckLocationResponseSerializer(result)
        return success_response(data=res_serializer.data)
