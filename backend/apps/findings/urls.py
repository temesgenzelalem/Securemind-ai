from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.findings.views import FindingViewSet

app_name = 'findings'

router = DefaultRouter()
router.register(r'', FindingViewSet, basename='finding')

urlpatterns = [
    path('', include(router.urls)),
]
