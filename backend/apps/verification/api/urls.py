from django.urls import path
from .views import (
    UserVerificationMeView,
    UserVerificationSubmitView,
    AdminVerificationQueueView,
    AdminVerificationDetailView,
    AdminVerificationApproveView,
    AdminVerificationSuspendView,
    AdminVerificationRejectView,
    AdminVerificationHistoryView,
)

urlpatterns = [
    path('me/', UserVerificationMeView.as_view(), name='verification-me'),
    path('me/submit/', UserVerificationSubmitView.as_view(), name='verification-submit'),
    path('admin/verifications/', AdminVerificationQueueView.as_view(), name='admin-verification-queue'),
    path('admin/verifications/<uuid:pk>/', AdminVerificationDetailView.as_view(), name='admin-verification-detail'),
    path('admin/verifications/<uuid:pk>/approve/', AdminVerificationApproveView.as_view(), name='admin-verification-approve'),
    path('admin/verifications/<uuid:pk>/suspend/', AdminVerificationSuspendView.as_view(), name='admin-verification-suspend'),
    path('admin/verifications/<uuid:pk>/reject/', AdminVerificationRejectView.as_view(), name='admin-verification-reject'),
    path('admin/verifications/<uuid:pk>/history/', AdminVerificationHistoryView.as_view(), name='admin-verification-history'),
]
