from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.remediation.views import RemediationViewSet

app_name = 'remediation'

router = DefaultRouter()
router.register(r'', RemediationViewSet, basename='remediation')

urlpatterns = [
    path('', include(router.urls)),
]
