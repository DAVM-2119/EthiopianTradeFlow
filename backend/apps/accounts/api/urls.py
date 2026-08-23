from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    CustomTokenRefreshView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='auth-token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('password/change/', PasswordChangeView.as_view(), name='auth-password-change'),
    path('password/reset/request/', PasswordResetRequestView.as_view(), name='auth-password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]
