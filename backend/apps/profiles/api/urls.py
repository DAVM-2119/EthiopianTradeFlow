from django.urls import path
from .views import UserProfileMeView, TransporterDriverListView

urlpatterns = [
    path('me/', UserProfileMeView.as_view(), name='profile-me'),
    path('transporter/drivers/', TransporterDriverListView.as_view(), name='transporter-drivers'),
]
