from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer, GenerateReportSerializer
from apps.authentication.permissions import TenantObjectPermission
from apps.audit.models import AuditLog

class ReportViewSet(viewsets.ModelViewSet):
    """
    Security Report Management (FR-REPORT-001 through FR-REPORT-007).
    """
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Report.objects.none()

        qs = Report.objects.select_related('scan__asset', 'generated_by')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return GenerateReportSerializer
        return ReportSerializer

    def perform_create(self, serializer):
        user = self.request.user
        scan = serializer.validated_data['scan']
        
        # Calculate instant findings metrics summary
        findings = scan.findings.all()
        metrics = {
            'total_findings': findings.count(),
            'critical': findings.filter(severity='critical').count(),
            'high': findings.filter(severity='high').count(),
            'medium': findings.filter(severity='medium').count(),
            'low': findings.filter(severity='low').count(),
            'confirmed_count': findings.filter(verification_status='confirmed').count(),
            'target_domain': scan.asset.domain
        }

        report = serializer.save(
            organization=scan.organization,
            generated_by=user,
            status=Report.Status.COMPLETED,
            metrics_summary=metrics
        )

        AuditLog.objects.create(
            organization=scan.organization,
            actor=user,
            action='report_generated',
            target_type='Report',
            target_id=str(report.id),
            details={'report_type': report.report_type, 'scan_id': str(scan.id)}
        )
