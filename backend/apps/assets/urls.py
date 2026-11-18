from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.assets.views import AssetViewSet, ScopeRuleViewSet

app_name = 'assets'

router = DefaultRouter()
router.register(r'scope-rules', ScopeRuleViewSet, basename='scope-rule')
router.register(r'', AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
