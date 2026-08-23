from django.urls import path
from .views import VehicleListCreateView, VehicleDetailView

urlpatterns = [
    path('', VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('<uuid:pk>/', VehicleDetailView.as_view(), name='vehicle-detail'),
]
