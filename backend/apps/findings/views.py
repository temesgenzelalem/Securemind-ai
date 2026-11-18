from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.findings.models import Finding
from apps.findings.serializers import FindingSerializer
from apps.authentication.permissions import TenantObjectPermission

class FindingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Centralized Vulnerability Finding Repository (FR-FIND-001).
    Supports comprehensive filtering by severity, verification status, and asset.
    """
    serializer_class = FindingSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('severity', 'verification_status', 'scan', 'asset', 'source_scanner')
    search_fields = ('title', 'description', 'affected_url', 'cwe_id')
    ordering_fields = ('created_at', 'severity', 'confidence_score')
    ordering = ('-created_at',)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Finding.objects.none()

        qs = Finding.objects.prefetch_related('evidences').select_related('remediation')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs
