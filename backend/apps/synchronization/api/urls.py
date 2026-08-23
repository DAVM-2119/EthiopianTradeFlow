from django.urls import path
from .views import (
    SyncEventSubmitAPIView,
    BatchSyncSubmitAPIView,
    SyncEventDetailAPIView,
    SyncEventRetryAPIView,
    SyncStatusSummaryAPIView,
)

urlpatterns = [
    path('events/', SyncEventSubmitAPIView.as_view(), name='sync-events-submit'),
    path('events/batch/', BatchSyncSubmitAPIView.as_view(), name='sync-events-batch'),
    path('events/<uuid:client_event_id>/', SyncEventDetailAPIView.as_view(), name='sync-events-detail'),
    path('events/<uuid:client_event_id>/retry/', SyncEventRetryAPIView.as_view(), name='sync-events-retry'),
    path('status/', SyncStatusSummaryAPIView.as_view(), name='sync-status-summary'),
]
