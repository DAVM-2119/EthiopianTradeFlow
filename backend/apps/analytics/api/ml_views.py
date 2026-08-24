from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from ml.common.model_registry import model_registry
from ml.eta.predictor import MLETAPredictor
from apps.eta.predictors.base import ETAContext
from django.utils import timezone
from datetime import datetime

class MLModelListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        active_eta = model_registry.get_active_model("eta")
        active_info = None
        if active_eta:
            meta = active_eta['metadata']
            active_info = meta.to_dict()

        return Response({
            'active_models': {
                'eta': active_info
            },
            'all_models': model_registry.list_models()
        })


class MLETAPredictView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        context = ETAContext(
            shipment_id=str(data.get('shipment_id', 'sim-001')),
            origin_city=data.get('origin_city', 'Djibouti Port'),
            destination_city=data.get('destination_city', 'Modjo Dry Port'),
            current_latitude=float(data.get('latitude', 11.5883)),
            current_longitude=float(data.get('longitude', 43.1450)),
            current_speed_kmh=float(data.get('speed', 62.0)),
            recent_average_speed_kmh=float(data.get('recent_avg_speed', 60.0)),
            known_delay_minutes=int(data.get('delay_minutes', 0)),
            timestamp=timezone.now()
        )

        predictor = MLETAPredictor()
        result = predictor.predict(context)

        return Response({
            'estimated_arrival': result.estimated_arrival.isoformat(),
            'remaining_distance_km': float(result.remaining_distance_km),
            'expected_speed_kmh': float(result.expected_speed_kmh),
            'delay_minutes': result.delay_minutes,
            'prediction_method': result.prediction_method,
            'algorithm_version': result.algorithm_version,
            'confidence': float(result.confidence)
        })
