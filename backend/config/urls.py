from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/auth/', include('apps.accounts.api.urls')),
    path('api/v1/profiles/', include('apps.profiles.api.urls')),
    path('api/v1/vehicles/', include('apps.fleet.api.urls')),
    path('api/v1/verification/', include('apps.verification.api.urls')),
    path('api/v1/loads/', include('apps.marketplace.api.urls')),
    path('api/v1/', include('apps.matching.api.urls')),
    path('api/v1/shipments/', include('apps.shipments.api.urls')),
    path('api/v1/tracking/', include('apps.tracking.api.urls')),
    path('api/v1/', include('apps.tracking.api.urls')),
    path('api/v1/sync/', include('apps.synchronization.api.urls')),
    
    # OpenAPI Schema documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
