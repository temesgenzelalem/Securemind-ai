from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from apps.scans.models import Scan
from apps.findings.models import Finding

class ScanComparisonService:
    """
    Assessment History & Recurring Vulnerability Diffing Service (FR-MON-004, FR-MON-005).
    Compares two scans on an asset using SHA-256 finding fingerprints to detect:
    - New findings (regression / newly introduced vulnerabilities)
    - Resolved findings (successful remediations)
    - Persistent / recurring findings (unpatched vulnerabilities across assessments)
    """

    @classmethod
    def compare_scans(cls, target_scan: Scan, baseline_scan: Optional[Scan] = None) -> Dict[str, Any]:
        """
        Compares target_scan against baseline_scan.
        If baseline_scan is not specified, selects the most recent prior completed scan for the same asset.
        """
        if baseline_scan is None:
            baseline_scan = (
                Scan.objects.filter(
                    asset=target_scan.asset,
                    status=Scan.Status.COMPLETED
                )
                .exclude(id=target_scan.id)
                .filter(created_at__lt=target_scan.created_at)
                .order_by('-created_at')
                .first()
            )

        target_findings = list(target_scan.findings.all())

        if baseline_scan is None:
            return {
                "has_baseline": False,
                "target_scan": {
                    "id": str(target_scan.id),
                    "scan_type": target_scan.scan_type,
                    "created_at": target_scan.created_at.isoformat(),
                    "total_findings": len(target_findings),
                },
                "baseline_scan": None,
                "summary": {
                    "new_count": len(target_findings),
                    "resolved_count": 0,
                    "recurring_count": 0,
                    "net_change": len(target_findings),
                    "posture_trend": "initial_baseline",
                },
                "new_findings": [cls._serialize_finding(f) for f in target_findings],
                "resolved_findings": [],
                "recurring_findings": [],
            }

        baseline_findings = list(baseline_scan.findings.all())

        target_by_fp = {f.fingerprint: f for f in target_findings if f.fingerprint}
        baseline_by_fp = {f.fingerprint: f for f in baseline_findings if f.fingerprint}

        target_fps = set(target_by_fp.keys())
        baseline_fps = set(baseline_by_fp.keys())

        new_fps = target_fps - baseline_fps
        resolved_fps = baseline_fps - target_fps
        recurring_fps = target_fps & baseline_fps

        new_list = [cls._serialize_finding(target_by_fp[fp]) for fp in new_fps]
        resolved_list = [cls._serialize_finding(baseline_by_fp[fp]) for fp in resolved_fps]
        recurring_list = [cls._serialize_finding(target_by_fp[fp]) for fp in recurring_fps]

        new_count = len(new_list)
        resolved_count = len(resolved_list)
        recurring_count = len(recurring_list)
        net_change = new_count - resolved_count

        if resolved_count > new_count:
            posture_trend = "improved"
        elif new_count > resolved_count:
            posture_trend = "degraded"
        else:
            posture_trend = "unchanged"

        # Severity breakdown
        severity_delta: Dict[str, Dict[str, int]] = {
            "critical": {"new": 0, "resolved": 0, "recurring": 0},
            "high": {"new": 0, "resolved": 0, "recurring": 0},
            "medium": {"new": 0, "resolved": 0, "recurring": 0},
            "low": {"new": 0, "resolved": 0, "recurring": 0},
            "informational": {"new": 0, "resolved": 0, "recurring": 0},
        }

        for item in new_list:
            sev = item.get("severity", "medium").lower()
            if sev in severity_delta:
                severity_delta[sev]["new"] += 1

        for item in resolved_list:
            sev = item.get("severity", "medium").lower()
            if sev in severity_delta:
                severity_delta[sev]["resolved"] += 1

        for item in recurring_list:
            sev = item.get("severity", "medium").lower()
            if sev in severity_delta:
                severity_delta[sev]["recurring"] += 1

        return {
            "has_baseline": True,
            "target_scan": {
                "id": str(target_scan.id),
                "scan_type": target_scan.scan_type,
                "created_at": target_scan.created_at.isoformat(),
                "total_findings": len(target_findings),
            },
            "baseline_scan": {
                "id": str(baseline_scan.id),
                "scan_type": baseline_scan.scan_type,
                "created_at": baseline_scan.created_at.isoformat(),
                "total_findings": len(baseline_findings),
            },
            "summary": {
                "new_count": new_count,
                "resolved_count": resolved_count,
                "recurring_count": recurring_count,
                "net_change": net_change,
                "posture_trend": posture_trend,
                "severity_delta": severity_delta,
            },
            "new_findings": new_list,
            "resolved_findings": resolved_list,
            "recurring_findings": recurring_list,
        }

    @classmethod
    def get_asset_history(cls, asset_id: str) -> List[Dict[str, Any]]:
        """
        Returns chronological assessment history for an asset with finding progression.
        """
        scans = (
            Scan.objects.filter(asset_id=asset_id, status=Scan.Status.COMPLETED)
            .order_by("created_at")
            .prefetch_related("findings")
        )

        history = []
        for scan in scans:
            findings = list(scan.findings.all())
            history.append({
                "scan_id": str(scan.id),
                "scan_type": scan.scan_type,
                "created_at": scan.created_at.isoformat(),
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "total_findings": len(findings),
                "critical": sum(1 for f in findings if f.severity == Finding.Severity.CRITICAL),
                "high": sum(1 for f in findings if f.severity == Finding.Severity.HIGH),
                "medium": sum(1 for f in findings if f.severity == Finding.Severity.MEDIUM),
                "low": sum(1 for f in findings if f.severity == Finding.Severity.LOW),
                "informational": sum(1 for f in findings if f.severity == Finding.Severity.INFORMATIONAL),
            })
        return history

    @staticmethod
    def _serialize_finding(finding: Finding) -> Dict[str, Any]:
        return {
            "id": str(finding.id),
            "fingerprint": finding.fingerprint,
            "title": finding.title,
            "severity": finding.severity,
            "verification_status": finding.verification_status,
            "confidence_score": finding.confidence_score,
            "affected_url": finding.affected_url,
            "parameter": finding.parameter,
            "cwe_id": finding.cwe_id,
            "cvss_score": finding.cvss_score,
            "source_scanner": finding.source_scanner,
        }
