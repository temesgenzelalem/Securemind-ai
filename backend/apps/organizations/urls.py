from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.organizations.views import OrganizationViewSet, ProjectViewSet

app_name = 'organizations'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('', include(router.urls)),
]
