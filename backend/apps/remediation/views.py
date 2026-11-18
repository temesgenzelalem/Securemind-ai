from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from apps.remediation.models import Remediation
from apps.remediation.serializers import RemediationSerializer, UpdateRemediationStatusSerializer
from apps.authentication.permissions import TenantObjectPermission, IsDeveloperOrAbove
from apps.audit.models import AuditLog

class RemediationViewSet(viewsets.ModelViewSet):
    """
    Remediation Center (FR-REMED-001 through FR-REMED-006).
    Allows developers and security engineers to review AI guidance and track fix lifecycle.
    """
    serializer_class = RemediationSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission, IsDeveloperOrAbove)
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Remediation.objects.none()

        qs = Remediation.objects.select_related('finding', 'assigned_to', 'resolved_by')
        if not user.is_superuser:
            qs = qs.filter(finding__organization=org)
        return qs

    def get_serializer_class(self):
        if self.action in ('partial_update', 'update'):
            return UpdateRemediationStatusSerializer
        return RemediationSerializer

    def perform_update(self, serializer):
        user = self.request.user
        new_status = serializer.validated_data.get('status')
        instance = serializer.instance

        if new_status in (Remediation.Status.FIXED, Remediation.Status.ACCEPTED_RISK):
            instance.resolved_by = user
            instance.resolved_at = timezone.now()

        instance = serializer.save()

        AuditLog.objects.create(
            organization=instance.finding.organization,
            actor=user,
            action='remediation_status_updated',
            target_type='Remediation',
            target_id=str(instance.id),
            details={'status': new_status, 'finding': instance.finding.title}
        )
