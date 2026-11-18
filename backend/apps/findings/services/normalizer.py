import hashlib
import logging
from django.utils import timezone
from apps.findings.models import Finding, Evidence
from apps.scans.models import Scan

logger = logging.getLogger(__name__)

class FindingNormalizerService:
    """
    Normalizes diverse scanner outputs (OWASP ZAP, Nuclei) into the platform's
    unified Finding and Evidence data structures, performing automated deduplication.
    """
    @staticmethod
    def normalize_zap_alerts(scan: Scan, raw_alerts: list[dict]) -> list[Finding]:
        severity_map = {
            'High': Finding.Severity.HIGH,
            'Medium': Finding.Severity.MEDIUM,
            'Low': Finding.Severity.LOW,
            'Informational': Finding.Severity.INFORMATIONAL,
        }

        created_findings = []
        for alert in raw_alerts:
            title = alert.get('alert', 'Unknown Vulnerability')
            affected_url = alert.get('url', scan.asset.base_url)
            parameter = alert.get('param', '')
            cwe_id = f"CWE-{alert.get('cweid')}" if alert.get('cweid') and alert.get('cweid') != '-1' else ""
            raw_severity = alert.get('risk', 'Medium')
            severity = severity_map.get(raw_severity, Finding.Severity.MEDIUM)

            fingerprint = hashlib.sha256(f"{title}|{affected_url}|{parameter}".encode('utf-8')).hexdigest()

            finding, created = Finding.objects.get_or_create(
                scan=scan,
                asset=scan.asset,
                organization=scan.organization,
                fingerprint=fingerprint,
                defaults={
                    'title': title,
                    'description': alert.get('description', ''),
                    'vulnerability_category': alert.get('name', 'Web Application Security'),
                    'cwe_id': cwe_id,
                    'severity': severity,
                    'verification_status': Finding.VerificationStatus.UNVERIFIED,
                    'confidence_score': 0.6,
                    'source_scanner': 'owasp_zap',
                    'affected_url': affected_url,
                    'http_method': alert.get('method', 'GET'),
                    'parameter': parameter,
                }
            )

            # Attach Evidence
            Evidence.objects.create(
                finding=finding,
                evidence_type=Evidence.EvidenceType.HTTP_TRAFFIC,
                raw_http_request=alert.get('request', ''),
                raw_http_response=alert.get('response', ''),
                payload_used=alert.get('attack', ''),
                extracted_proof=alert.get('evidence', ''),
                verification_notes=f"Reported by ZAP with original confidence: {alert.get('confidence')}"
            )

            created_findings.append(finding)
        return created_findings

    @staticmethod
    def normalize_nuclei_findings(scan: Scan, raw_results: list[dict]) -> list[Finding]:
        severity_map = {
            'critical': Finding.Severity.CRITICAL,
            'high': Finding.Severity.HIGH,
            'medium': Finding.Severity.MEDIUM,
            'low': Finding.Severity.LOW,
            'info': Finding.Severity.INFORMATIONAL,
        }

        created_findings = []
        for result in raw_results:
            info = result.get('info', {})
            title = info.get('name', result.get('template-id', 'Nuclei Finding'))
            affected_url = result.get('matched-at', scan.asset.base_url)
            raw_severity = info.get('severity', 'medium').lower()
            severity = severity_map.get(raw_severity, Finding.Severity.MEDIUM)

            classification = info.get('classification', {})
            cwe_list = classification.get('cwe-id', [])
            cwe_id = cwe_list[0] if isinstance(cwe_list, list) and cwe_list else ""
            cvss_metrics = classification.get('cvss-metrics', '')
            cvss_score = classification.get('cvss-score', None)

            fingerprint = hashlib.sha256(f"{title}|{affected_url}".encode('utf-8')).hexdigest()

            finding, created = Finding.objects.get_or_create(
                scan=scan,
                asset=scan.asset,
                organization=scan.organization,
                fingerprint=fingerprint,
                defaults={
                    'title': title,
                    'description': info.get('description', ''),
                    'vulnerability_category': 'Template Detection',
                    'cwe_id': cwe_id,
                    'cvss_vector': cvss_metrics,
                    'cvss_score': cvss_score,
                    'severity': severity,
                    'verification_status': Finding.VerificationStatus.UNVERIFIED,
                    'confidence_score': 0.7,
                    'source_scanner': 'nuclei',
                    'affected_url': affected_url,
                    'http_method': 'GET',
                }
            )

            Evidence.objects.create(
                finding=finding,
                evidence_type=Evidence.EvidenceType.HTTP_TRAFFIC,
                raw_http_request=result.get('request', ''),
                raw_http_response=result.get('response', ''),
                extracted_proof=str(result.get('extracted-results', '')),
                verification_notes=f"Triggered Nuclei template: {result.get('template-id')}"
            )

            created_findings.append(finding)
        return created_findings
