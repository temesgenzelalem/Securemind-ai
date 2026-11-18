from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.scans.models import Scan
from apps.scans.serializers import ScanSerializer, CreateScanSerializer
from apps.scans.tasks import execute_assessment_workflow
from apps.authentication.permissions import TenantObjectPermission, IsSecurityAnalystOrAbove
from apps.audit.models import AuditLog

class ScanViewSet(viewsets.ModelViewSet):
    serializer_class = ScanSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

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
