import logging
from celery import shared_task
from django.utils import timezone
from apps.scans.models import Scan, ScannerExecution
from apps.assets.models import Asset
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

    except Exception as e:
        logger.exception(f"Unhandled exception during scan {scan_id}: {e}")
        scan.status = Scan.Status.FAILED
        scan.error_message = str(e)
        scan.save(update_fields=['status', 'error_message'])
