from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # SecureMind AI API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/assets/', include('apps.assets.urls')),
    path('api/v1/scans/', include('apps.scans.urls')),
    path('api/v1/findings/', include('apps.findings.urls')),
    path('api/v1/remediation/', include('apps.remediation.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]
