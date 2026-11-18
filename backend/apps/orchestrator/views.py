from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.orchestrator.models import AgentExecution, WorkflowState
from apps.orchestrator.serializers import AgentExecutionSerializer, WorkflowStateSerializer
from apps.authentication.permissions import TenantObjectPermission

class AgentExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    AI Agent Execution Telemetry (SRS Section 4.6 & 6.2).
    Inspect inputs, outputs, models used, tokens, and latency across all 6 specialized agents.
    """
    serializer_class = AgentExecutionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('agent_name', 'status', 'scan')
    search_fields = ('agent_name', 'model_used', 'error_message')
    ordering_fields = ('created_at', 'execution_time_seconds', 'tokens_used')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return AgentExecution.objects.none()

        qs = AgentExecution.objects.select_related('scan')
        if not user.is_superuser:
            qs = qs.filter(scan__organization=org)
        return qs

class WorkflowStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Assessment Workflow State Monitoring.
    """
    serializer_class = WorkflowStateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return WorkflowState.objects.none()

        qs = WorkflowState.objects.select_related('scan')
        if not user.is_superuser:
            qs = qs.filter(scan__organization=org)
        return qs
