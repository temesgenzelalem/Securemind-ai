from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.scans.views import (
    ScanScheduleViewSet,
    AssessmentNotificationViewSet,
    MonitoringStatsView
)

router = DefaultRouter()
router.register(r'schedules', ScanScheduleViewSet, basename='monitoring-schedules')
router.register(r'notifications', AssessmentNotificationViewSet, basename='monitoring-notifications')

urlpatterns = [
    path('stats/', MonitoringStatsView.as_view(), name='monitoring-stats'),
    path('overview/', MonitoringStatsView.as_view(), name='monitoring-overview'),
    path('', include(router.urls)),
]
