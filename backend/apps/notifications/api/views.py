from rest_framework import generics, status, permissions
from rest_framework.response import Response
from apps.core.responses import success_response, error_response
from apps.core.exceptions import NotFoundException
from apps.notifications.selectors import (
    get_user_notifications,
    get_notification_by_id,
    get_user_notification_preferences,
)
from apps.notifications.services import (
    mark_notification_as_read,
    mark_all_notifications_as_read,
    update_user_preference,
)
from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    UpdatePreferenceSerializer,
)
from apps.notifications.permissions import IsNotificationRecipient

class NotificationListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        unread_only = self.request.query_params.get('unread_only', 'false').lower() == 'true'
        return get_user_notifications(self.request.user, unread_only=unread_only)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="User notifications retrieved successfully.")


class NotificationDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsNotificationRecipient]
    serializer_class = NotificationSerializer

    def get_object(self):
        notification_id = self.kwargs.get('notification_id')
        obj = get_notification_by_id(notification_id, user=self.request.user)
        if not obj:
            raise NotFoundException("Notification not found.")
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return success_response(data=serializer.data, message="Notification detail retrieved successfully.")


class NotificationMarkReadAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id, *args, **kwargs):
        notification = mark_notification_as_read(
            notification_id=str(notification_id),
            user_id=str(request.user.id)
        )
        serializer = NotificationSerializer(notification)
        return success_response(data=serializer.data, message="Notification marked as read.")


class NotificationMarkAllReadAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        count = mark_all_notifications_as_read(user_id=str(request.user.id))
        return success_response(data={'marked_read_count': count}, message=f"{count} notifications marked as read.")


class PreferenceListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        return get_user_notification_preferences(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="User notification preferences retrieved.")


class PreferenceUpdateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePreferenceSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pref = update_user_preference(
            user_id=str(request.user.id),
            notification_type=serializer.validated_data['notification_type'],
            channel=serializer.validated_data['channel'],
            enabled=serializer.validated_data['enabled']
        )
        res_serializer = NotificationPreferenceSerializer(pref)
        return success_response(data=res_serializer.data, message="Notification preference updated.")
