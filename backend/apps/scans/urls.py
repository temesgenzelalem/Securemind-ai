from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.scans.views import ScanViewSet

app_name = 'scans'

router = DefaultRouter()
router.register(r'', ScanViewSet, basename='scan')

urlpatterns = [
    path('', include(router.urls)),
]
