from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orchestrator.views import AgentExecutionViewSet, WorkflowStateViewSet

app_name = 'orchestrator'

router = DefaultRouter()
router.register(r'executions', AgentExecutionViewSet, basename='agent-execution')
router.register(r'workflows', WorkflowStateViewSet, basename='workflow-state')

urlpatterns = [
    path('', include(router.urls)),
]
