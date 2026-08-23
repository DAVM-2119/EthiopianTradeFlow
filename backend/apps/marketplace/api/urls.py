from django.urls import path
from .views import (
    LoadListCreateView,
    LoadDetailView,
    LoadPostView,
    LoadCancelView,
    LoadBidsListCreateView,
    BidDetailView,
    BidWithdrawView,
    BidAcceptView,
    MyBidsListView,
)

urlpatterns = [
    # Load endpoints
    path('', LoadListCreateView.as_view(), name='load-list-create'),
    path('<uuid:pk>/', LoadDetailView.as_view(), name='load-detail'),
    path('<uuid:pk>/post/', LoadPostView.as_view(), name='load-post'),
    path('<uuid:pk>/cancel/', LoadCancelView.as_view(), name='load-cancel'),

    # Phase 8 Bidding & Booking endpoints
    path('<uuid:load_id>/bids/', LoadBidsListCreateView.as_view(), name='load-bids-list-create'),
    path('bids/<uuid:pk>/', BidDetailView.as_view(), name='bid-detail'),
    path('bids/<uuid:pk>/withdraw/', BidWithdrawView.as_view(), name='bid-withdraw'),
    path('bids/<uuid:pk>/accept/', BidAcceptView.as_view(), name='bid-accept'),
    path('my-bids/', MyBidsListView.as_view(), name='my-bids-list'),
]
