from rest_framework import viewsets, permissions
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.authentication.permissions import IsOrgAdmin

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit Trail (FR-SEC-006 & Section 8.5).
    Provides organization administrators with immutable logs of security-sensitive operations.
    """
    serializer_class = AuditLogSerializer
    permission_classes = (permissions.IsAuthenticated, IsOrgAdmin)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return AuditLog.objects.none()

        qs = AuditLog.objects.select_related('actor')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs
