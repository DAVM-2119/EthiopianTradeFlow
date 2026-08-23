from django.urls import path
from .views import (
    PaymentListCreateAPIView,
    PaymentDetailAPIView,
    PaymentInitiateAPIView,
    PaymentConfirmAPIView,
    PaymentWebhookAPIView,
    PayoutListAPIView,
    PayoutDetailAPIView,
    ProcessPayoutAPIView,
    SettlementListAPIView,
    SettlementDetailAPIView,
    DisputeListCreateAPIView,
    DisputeDetailAPIView,
    ResolveDisputeAPIView,
)

urlpatterns = [
    path('payments/', PaymentListCreateAPIView.as_view(), name='payment-list-create'),
    path('payments/<uuid:payment_id>/', PaymentDetailAPIView.as_view(), name='payment-detail'),
    path('payments/<uuid:payment_id>/initiate/', PaymentInitiateAPIView.as_view(), name='payment-initiate'),
    path('payments/<uuid:payment_id>/confirm/', PaymentConfirmAPIView.as_view(), name='payment-confirm'),
    path('payments/webhooks/provider/', PaymentWebhookAPIView.as_view(), name='payment-webhook'),

    path('payments/payouts/', PayoutListAPIView.as_view(), name='payout-list'),
    path('payments/payouts/<uuid:payout_id>/', PayoutDetailAPIView.as_view(), name='payout-detail'),
    path('payments/payouts/<uuid:payout_id>/process/', ProcessPayoutAPIView.as_view(), name='process-payout'),

    path('payments/settlements/', SettlementListAPIView.as_view(), name='settlement-list'),
    path('payments/settlements/<uuid:settlement_id>/', SettlementDetailAPIView.as_view(), name='settlement-detail'),

    path('payments/disputes/', DisputeListCreateAPIView.as_view(), name='dispute-list-create'),
    path('payments/disputes/<uuid:dispute_id>/', DisputeDetailAPIView.as_view(), name='dispute-detail'),
    path('payments/disputes/<uuid:dispute_id>/resolve/', ResolveDisputeAPIView.as_view(), name='resolve-dispute'),
]
