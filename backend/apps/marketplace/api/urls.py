from django.urls import path
from .views import (
    LoadListCreateView,
    LoadDetailView,
    LoadPostView,
    LoadCancelView,
)

urlpatterns = [
    path('', LoadListCreateView.as_view(), name='load-list-create'),
    path('<uuid:pk>/', LoadDetailView.as_view(), name='load-detail'),
    path('<uuid:pk>/post/', LoadPostView.as_view(), name='load-post'),
    path('<uuid:pk>/cancel/', LoadCancelView.as_view(), name='load-cancel'),
]
