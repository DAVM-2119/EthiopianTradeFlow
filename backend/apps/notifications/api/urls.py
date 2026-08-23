from django.urls import path
from .views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
    PreferenceListAPIView,
    PreferenceUpdateAPIView,
)

urlpatterns = [
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/read-all/', NotificationMarkAllReadAPIView.as_view(), name='notification-mark-all-read'),
    path('notifications/preferences/', PreferenceListAPIView.as_view(), name='preference-list'),
    path('notifications/preferences/update/', PreferenceUpdateAPIView.as_view(), name='preference-update'),
    path('notifications/<uuid:notification_id>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('notifications/<uuid:notification_id>/read/', NotificationMarkReadAPIView.as_view(), name='notification-mark-read'),
]
