from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException
from apps.synchronization.serializers import (
    OfflineSyncEventSerializer,
    OfflineSyncEventCreateSerializer,
    BatchSyncEventSerializer,
    SyncStatusSummarySerializer,
)
from apps.synchronization.services import (
    process_sync_event,
    process_batch_sync_events,
    retry_failed_sync_event,
)
from apps.synchronization.selectors import (
    get_sync_event_by_client_id,
    get_sync_status_summary,
)

class SyncEventSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OfflineSyncEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sync_event = process_sync_event(user=request.user, data=serializer.validated_data)
        out_serializer = OfflineSyncEventSerializer(sync_event)
        
        status_code = status.HTTP_201_CREATED if sync_event.attempt_count <= 1 else status.HTTP_200_OK
        return success_response(
            data=out_serializer.data,
            message="Offline sync event processed.",
            status_code=status_code
        )


class BatchSyncSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BatchSyncEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = process_batch_sync_events(user=request.user, events_data=serializer.validated_data['events'])
        return success_response(
            data={'results': results},
            message=f"Processed batch of {len(results)} sync events.",
            status_code=status.HTTP_200_OK
        )


class SyncEventDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, client_event_id):
        sync_event = get_sync_event_by_client_id(user=request.user, client_event_id=client_event_id)
        if not sync_event:
            raise NotFoundException("Offline sync event not found.")

        serializer = OfflineSyncEventSerializer(sync_event)
        return success_response(data=serializer.data)


class SyncEventRetryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_event_id):
        sync_event = retry_failed_sync_event(user=request.user, client_event_id=client_event_id)
        serializer = OfflineSyncEventSerializer(sync_event)
        return success_response(
            data=serializer.data,
            message="Sync event re-processed."
        )


class SyncStatusSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = get_sync_status_summary(user=request.user)
        serializer = SyncStatusSummarySerializer(summary)
        return success_response(data=serializer.data)
