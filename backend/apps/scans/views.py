from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.scans.models import Scan, ScanSchedule, AssessmentNotification
from apps.scans.serializers import (
    ScanSerializer,
    CreateScanSerializer,
    ScanScheduleSerializer,
    AssessmentNotificationSerializer
)
from apps.scans.tasks import execute_assessment_workflow
from apps.authentication.permissions import TenantObjectPermission, IsSecurityAnalystOrAbove
from apps.audit.models import AuditLog
from apps.findings.models import Finding
from apps.assets.models import Asset

class ScanViewSet(viewsets.ModelViewSet):
    serializer_class = ScanSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'approve', 'cancel'):
            return [permissions.IsAuthenticated(), IsSecurityAnalystOrAbove(), TenantObjectPermission()]
        return [permissions.IsAuthenticated(), TenantObjectPermission()]

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Scan.objects.none()

        qs = Scan.objects.filter(is_active=True).select_related('asset').prefetch_related('scanner_executions', 'findings')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateScanSerializer
        return ScanSerializer

    def perform_create(self, serializer):
        user = self.request.user
        org = user.current_organization
        scan_type = serializer.validated_data.get('scan_type', Scan.ScanType.PASSIVE)
        
        requires_approval = scan_type in (Scan.ScanType.CONTROLLED_ACTIVE, Scan.ScanType.COMPREHENSIVE)

        scan = serializer.save(
            organization=org,
            created_by=user,
            requires_approval=requires_approval,
            is_approved=not requires_approval,
            status=Scan.Status.AUTHORIZATION_REVIEW if requires_approval else Scan.Status.QUEUED
        )

        AuditLog.objects.create(
            organization=org,
            actor=user,
            action='scan_created',
            target_type='Scan',
            target_id=str(scan.id),
            details={'scan_type': scan_type, 'asset': scan.asset.domain, 'requires_approval': requires_approval}
        )

        # Dispatch async Celery pipeline immediately if already approved
        if not requires_approval:
            execute_assessment_workflow.delay(str(scan.id))

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSecurityAnalystOrAbove])
    def approve(self, request, pk=None):
        """Human-in-the-loop sign-off for active/intrusive scans."""
        scan = self.get_object()
        if scan.status not in (Scan.Status.AUTHORIZATION_REVIEW, Scan.Status.PENDING):
            return Response({'error': f"Cannot approve scan in status '{scan.status}'."}, status=status.HTTP_400_BAD_REQUEST)

        scan.is_approved = True
        scan.approved_by = request.user
        scan.status = Scan.Status.QUEUED
        scan.save(update_fields=['is_approved', 'approved_by', 'status'])

        AuditLog.objects.create(
            organization=scan.organization,
            actor=request.user,
            action='scan_approved',
            target_type='Scan',
            target_id=str(scan.id)
        )

        execute_assessment_workflow.delay(str(scan.id))
        return Response({'message': 'Scan approved and queued for execution.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancels a queued or running scan."""
        scan = self.get_object()
        if scan.status in (Scan.Status.COMPLETED, Scan.Status.FAILED, Scan.Status.CANCELLED):
            return Response({'error': f"Scan is already in terminal state '{scan.status}'."}, status=status.HTTP_400_BAD_REQUEST)

        scan.status = Scan.Status.CANCELLED
        scan.save(update_fields=['status'])

        AuditLog.objects.create(
            organization=scan.organization,
            actor=request.user,
            action='scan_cancelled',
            target_type='Scan',
            target_id=str(scan.id)
        )

        return Response({'message': 'Scan assessment cancelled.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        """Compares assessment findings against a baseline scan (FR-MON-004, FR-MON-005)."""
        scan = self.get_object()
        baseline_id = request.query_params.get('with')
        baseline_scan = None
        if baseline_id:
            try:
                baseline_scan = Scan.objects.get(id=baseline_id, organization=scan.organization)
            except Scan.DoesNotExist:
                return Response({'error': f"Baseline scan '{baseline_id}' not found."}, status=status.HTTP_404_NOT_FOUND)

        from apps.scans.services.comparison import ScanComparisonService
        diff = ScanComparisonService.compare_scans(target_scan=scan, baseline_scan=baseline_scan)
        return Response(diff, status=status.HTTP_200_OK)


class ScanScheduleViewSet(viewsets.ModelViewSet):
    """
    Recurring Assessment Schedule Management (FR-MON-001).
    Allows organizations to create, pause, update, or remove recurring scan schedules.
    """
    serializer_class = ScanScheduleSerializer
    permission_classes = (permissions.IsAuthenticated, IsSecurityAnalystOrAbove)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return ScanSchedule.objects.none()

        qs = ScanSchedule.objects.filter(is_active=True).select_related('asset')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        org = user.current_organization
        schedule = serializer.save(organization=org, created_by=user)
        AuditLog.objects.create(
            organization=org,
            actor=user,
            action='schedule_created',
            target_type='ScanSchedule',
            target_id=str(schedule.id),
            details={'asset': schedule.asset.domain, 'frequency': schedule.frequency, 'scan_type': schedule.scan_type}
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            organization=instance.organization,
            actor=self.request.user,
            action='schedule_deleted',
            target_type='ScanSchedule',
            target_id=str(instance.id),
            details={'asset': instance.asset.domain, 'frequency': instance.frequency}
        )
        instance.delete()


class AssessmentNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Assessment & Critical Vulnerability Notifications (FR-MON-002, FR-MON-003).
    """
    serializer_class = AssessmentNotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return AssessmentNotification.objects.none()

        qs = AssessmentNotification.objects.filter(organization=org)
        return qs.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'})


class MonitoringStatsView(APIView):
    """
    Aggregated Monitoring & Posture Statistics (FR-MON-004, FR-MON-005).
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Response({'error': 'No active organization selected.'}, status=status.HTTP_400_BAD_REQUEST)

        org_filter = {'organization': org} if not user.is_superuser else {}

        total_assets = Asset.objects.filter(is_active=True, **org_filter).count()
        verified_assets = Asset.objects.filter(verification_status=Asset.VerificationStatus.VERIFIED, is_active=True, **org_filter).count()
        total_scans = Scan.objects.filter(is_active=True, **org_filter).count()
        active_schedules = ScanSchedule.objects.filter(is_active=True, **org_filter).count()
        unread_notifications = AssessmentNotification.objects.filter(is_read=False, **org_filter).count()

        # Vulnerabilities count
        findings_qs = Finding.objects.filter(**org_filter)
        total_findings = findings_qs.count()
        critical_count = findings_qs.filter(severity=Finding.Severity.CRITICAL).count()
        high_count = findings_qs.filter(severity=Finding.Severity.HIGH).count()
        medium_count = findings_qs.filter(severity=Finding.Severity.MEDIUM).count()
        low_count = findings_qs.filter(severity=Finding.Severity.LOW).count()

        return Response({
            'total_assets': total_assets,
            'verified_assets': verified_assets,
            'total_scans': total_scans,
            'active_schedules': active_schedules,
            'unread_notifications': unread_notifications,
            'findings_summary': {
                'total': total_findings,
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count,
            }
        }, status=status.HTTP_200_OK)

