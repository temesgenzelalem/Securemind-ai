from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer, GenerateReportSerializer
from apps.reports.services.pdf_generator import SecurityReportPDFGenerator
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(ReportSerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers)

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
            status=Report.Status.GENERATING,
            metrics_summary=metrics
        )

        # Generate actual PDF file
        try:
            pdf_content = SecurityReportPDFGenerator.generate_pdf_report(report)
            report.pdf_file.save(f"report_{report.id}.pdf", pdf_content, save=False)
            report.status = Report.Status.COMPLETED
            report.save(update_fields=['pdf_file', 'status'])
        except Exception as e:
            report.status = Report.Status.FAILED
            report.error_message = str(e)
            report.save(update_fields=['status', 'error_message'])

        AuditLog.objects.create(
            organization=scan.organization,
            actor=user,
            action='report_generated',
            target_type='Report',
            target_id=str(report.id),
            details={'report_type': report.report_type, 'scan_id': str(scan.id)}
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Streams authorized PDF security assessment report."""
        report = self.get_object()
        if not report.pdf_file or not report.pdf_file.storage.exists(report.pdf_file.name):
            # Regenerate if not stored
            pdf_content = SecurityReportPDFGenerator.generate_pdf_report(report)
            report.pdf_file.save(f"report_{report.id}.pdf", pdf_content, save=True)

        response = HttpResponse(report.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="securemind_report_{report.scan.asset.domain}_{report.id}.pdf"'
        
        AuditLog.objects.create(
            organization=report.organization,
            actor=request.user,
            action='report_downloaded',
            target_type='Report',
            target_id=str(report.id)
        )
        return response
