import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from apps.scans.models import Scan, ScannerExecution, ScanSchedule, AssessmentNotification
from apps.assets.models import Asset
from apps.findings.models import Finding
from apps.audit.models import AuditLog
from apps.scans.services.zap_service import ZAPScannerService
from apps.scans.services.nuclei_service import NucleiScannerService
from apps.findings.services.normalizer import FindingNormalizerService
from apps.orchestrator.services.orchestrator_engine import OrchestratorEngine

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=1)
def execute_assessment_workflow(self, scan_id: str):
    """
    Main asynchronous pipeline for coordinating a SecureMind AI assessment.
    Enforces authorization, runs scanners, normalizes outputs, and invokes AI agents.
    """
    try:
        scan = Scan.objects.select_related('asset', 'organization').get(id=scan_id)
    except Scan.DoesNotExist:
        logger.error(f"Scan {scan_id} does not exist.")
        return

    # 1. Deterministic Authorization Guard
    if not scan.asset.is_authorized:
        scan.status = Scan.Status.FAILED
        scan.error_message = "Scan aborted: Target asset ownership has not been verified or authorization has expired."
        scan.save(update_fields=['status', 'error_message'])
        return

    # Check if scan requires human approval and has not received it
    if scan.requires_approval and not scan.is_approved:
        scan.status = Scan.Status.AUTHORIZATION_REVIEW
        scan.save(update_fields=['status'])
        return

    scan.status = Scan.Status.RUNNING
    scan.started_at = timezone.now()
    scan.save(update_fields=['status', 'started_at'])

    try:
        zap_service = ZAPScannerService()
        nuclei_service = NucleiScannerService()

        # 2. OWASP ZAP Execution
        zap_exec = ScannerExecution.objects.create(
            scan=scan,
            scanner_type=ScannerExecution.ScannerType.OWASP_ZAP,
            status=ScannerExecution.ExecutionStatus.RUNNING,
            started_at=timezone.now()
        )

        raw_zap_alerts = []
        if zap_service.is_available():
            # Spider target
            spider_id = zap_service.start_spider(scan.asset.base_url)
            # Wait for passive scanner records to complete
            zap_service.wait_for_passive_scan(timeout_seconds=30)

            # Controlled Active scan if permitted
            if scan.scan_type in (Scan.ScanType.CONTROLLED_ACTIVE, Scan.ScanType.COMPREHENSIVE):
                ascan_id = zap_service.start_active_scan(scan.asset.base_url)

            raw_zap_alerts = zap_service.get_alerts(scan.asset.base_url)
            zap_exec.status = ScannerExecution.ExecutionStatus.COMPLETED
            zap_exec.raw_output = {'alerts_count': len(raw_zap_alerts)}
        else:
            zap_exec.status = ScannerExecution.ExecutionStatus.COMPLETED
            zap_exec.execution_stats = {'note': 'ZAP daemon offline or mock mode.'}

        zap_exec.completed_at = timezone.now()
        zap_exec.save()

        # 3. Nuclei Execution
        nuclei_exec = ScannerExecution.objects.create(
            scan=scan,
            scanner_type=ScannerExecution.ScannerType.NUCLEI,
            status=ScannerExecution.ExecutionStatus.RUNNING,
            started_at=timezone.now()
        )

        raw_nuclei_results = nuclei_service.execute_scan(scan.asset.base_url)
        nuclei_exec.status = ScannerExecution.ExecutionStatus.COMPLETED
        nuclei_exec.completed_at = timezone.now()
        nuclei_exec.raw_output = {'findings_count': len(raw_nuclei_results)}
        nuclei_exec.save()

        # 4. Normalize Scanner Findings
        zap_findings = FindingNormalizerService.normalize_zap_alerts(scan, raw_zap_alerts)
        nuclei_findings = FindingNormalizerService.normalize_nuclei_findings(scan, raw_nuclei_results)
        all_findings = zap_findings + nuclei_findings

        # 5. AI Agent Pipeline (Orchestrator, Verification, Risk, Remediation)
        OrchestratorEngine.process_scan_findings(scan, all_findings)

        scan.status = Scan.Status.COMPLETED
        scan.completed_at = timezone.now()
        scan.save(update_fields=['status', 'completed_at'])

        # Audit log scan completion
        AuditLog.objects.create(
            organization=scan.organization,
            actor=scan.created_by,
            action='scan_completed',
            target_type='Scan',
            target_id=str(scan.id),
            details={
                'total_findings': len(all_findings),
                'asset': scan.asset.domain,
                'scan_type': scan.scan_type,
            }
        )

        # Notify user of completion (FR-MON-002)
        AssessmentNotification.objects.create(
            organization=scan.organization,
            recipient=scan.created_by,
            scan=scan,
            notification_type=AssessmentNotification.NotificationType.SCAN_COMPLETED,
            title=f"Security Assessment Completed: {scan.asset.domain}",
            message=f"Assessment finished successfully with {len(all_findings)} normalized findings.",
            severity=AssessmentNotification.SeverityLevel.INFO,
            details={'total_findings': len(all_findings), 'scan_type': scan.scan_type}
        )

        # Notify authorized users about important new/critical findings (FR-MON-003)
        critical_high = [f for f in all_findings if f.severity in (Finding.Severity.CRITICAL, Finding.Severity.HIGH)]
        if critical_high:
            AssessmentNotification.objects.create(
                organization=scan.organization,
                recipient=scan.created_by,
                scan=scan,
                notification_type=AssessmentNotification.NotificationType.CRITICAL_FINDING,
                title=f"High/Critical Vulnerabilities Detected on {scan.asset.domain}",
                message=f"Discovered {len(critical_high)} critical or high-risk findings that require attention.",
                severity=AssessmentNotification.SeverityLevel.CRITICAL,
                details={'critical_high_count': len(critical_high)}
            )

    except Exception as e:
        logger.exception(f"Unhandled exception during scan {scan_id}: {e}")
        scan.status = Scan.Status.FAILED
        scan.error_message = str(e)
        scan.save(update_fields=['status', 'error_message'])

        AuditLog.objects.create(
            organization=scan.organization,
            actor=scan.created_by,
            action='scan_failed',
            target_type='Scan',
            target_id=str(scan.id),
            details={'error': str(e), 'asset': scan.asset.domain}
        )

        AssessmentNotification.objects.create(
            organization=scan.organization,
            recipient=scan.created_by,
            scan=scan,
            notification_type=AssessmentNotification.NotificationType.SCAN_FAILED,
            title=f"Security Assessment Failed: {scan.asset.domain}",
            message=f"Scan encountered an error: {str(e)[:200]}",
            severity=AssessmentNotification.SeverityLevel.WARNING,
            details={'error': str(e)}
        )


@shared_task
def run_scheduled_assessments():
    """
    Celery Beat Periodic Task (FR-MON-001).
    Evaluates recurring assessment schedules and queues authorized scans.
    """
    now = timezone.now()
    schedules = ScanSchedule.objects.filter(is_active=True, next_run_at__lte=now).select_related('asset', 'organization')
    triggered_count = 0

    for sched in schedules:
        if not sched.asset.is_authorized:
            logger.warning(f"Skipping scheduled scan for {sched.asset.domain}: asset not authorized or expired.")
            continue

        scan = Scan.objects.create(
            asset=sched.asset,
            organization=sched.organization,
            scan_type=sched.scan_type,
            created_by=sched.created_by,
            status=Scan.Status.QUEUED,
            requires_approval=False,
            is_approved=True,
        )

        AuditLog.objects.create(
            organization=sched.organization,
            actor=sched.created_by,
            action='scheduled_scan_triggered',
            target_type='Scan',
            target_id=str(scan.id),
            details={'schedule_id': str(sched.id), 'frequency': sched.frequency}
        )

        AssessmentNotification.objects.create(
            organization=sched.organization,
            recipient=sched.created_by,
            scan=scan,
            notification_type=AssessmentNotification.NotificationType.SCHEDULE_TRIGGERED,
            title=f"Recurring Assessment Started for {sched.asset.domain}",
            message=f"Scheduled {sched.frequency} security assessment has commenced.",
            severity=AssessmentNotification.SeverityLevel.INFO
        )

        execute_assessment_workflow.delay(str(scan.id))

        sched.last_run_at = now
        if sched.frequency == ScanSchedule.Frequency.DAILY:
            sched.next_run_at = now + timedelta(days=1)
        elif sched.frequency == ScanSchedule.Frequency.WEEKLY:
            sched.next_run_at = now + timedelta(weeks=1)
        elif sched.frequency == ScanSchedule.Frequency.MONTHLY:
            sched.next_run_at = now + timedelta(days=30)
        sched.save(update_fields=['last_run_at', 'next_run_at'])
        triggered_count += 1

    return f"Triggered {triggered_count} scheduled assessments."
