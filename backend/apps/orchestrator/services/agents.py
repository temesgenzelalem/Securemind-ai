import json
import logging
from apps.orchestrator.services.llm_client import LLMClient
from apps.findings.models import Finding, Evidence
from apps.remediation.models import Remediation

logger = logging.getLogger(__name__)

class AuthorizationAgent:
    """SMAI-AI-AGT-001: Evaluates authorization scope and flags intrusive operations."""
    @staticmethod
    def evaluate_scope(asset, requested_scan_type: str) -> dict:
        is_intrusive = requested_scan_type in ('controlled_active', 'comprehensive')
        return {
            'domain': asset.domain,
            'is_authorized': asset.is_authorized,
            'requires_human_approval': is_intrusive,
            'allowed_destinations': [asset.domain]
        }

class ReconnaissanceAgent:
    """SMAI-AI-AGT-002: Identifies application tech stack from response headers & patterns."""
    @staticmethod
    def analyze_tech_stack(asset, findings) -> dict:
        detected_stack = {
            'framework': 'Unknown',
            'server': 'Unknown',
            'language': 'Unknown',
        }
        # Check evidence headers
        for finding in findings[:10]:
            for ev in finding.evidences.all():
                resp = ev.raw_http_response.lower()
                if 'x-powered-by: next.js' in resp or '/_next/' in resp:
                    detected_stack['framework'] = 'Next.js'
                    detected_stack['language'] = 'TypeScript/JavaScript'
                elif 'csrftoken' in resp or 'django' in resp:
                    detected_stack['framework'] = 'Django'
                    detected_stack['language'] = 'Python'
                elif 'laravel' in resp or 'x-powered-by: php' in resp:
                    detected_stack['framework'] = 'Laravel'
                    detected_stack['language'] = 'PHP'
                elif 'server: nginx' in resp:
                    detected_stack['server'] = 'Nginx'
                elif 'server: cloudflare' in resp:
                    detected_stack['server'] = 'Cloudflare'
        return detected_stack

class VerificationAgent:
    """SMAI-AI-AGT-004: Cross-references finding against raw HTTP evidence to eliminate false positives."""
    @staticmethod
    def verify_finding(finding: Finding, llm_client: LLMClient) -> dict:
        evidence = finding.evidences.first()
        raw_req = evidence.raw_http_request if evidence else ""
        raw_resp = evidence.raw_http_response if evidence else ""
        payload = evidence.payload_used if evidence else ""

        system_instruction = (
            "You are the SecureMind AI Verification Agent. Your sole purpose is to evaluate whether "
            "technical evidence (HTTP request/response) confirms a security vulnerability or if it is a false positive. "
            "Return valid JSON with keys: verification_status (Confirmed | Likely | Unverified | False Positive | Needs Manual Review), "
            "confidence_score (0.0 to 1.0), is_false_positive (bool), and evidence_analysis (string)."
        )

        prompt = (
            f"Vulnerability Title: {finding.title}\n"
            f"Category: {finding.vulnerability_category}\n"
            f"Affected URL: {finding.affected_url}\n"
            f"Parameter: {finding.parameter}\n"
            f"Payload Used: {payload}\n\n"
            f"--- HTTP REQUEST ---\n{raw_req[:1500]}\n\n"
            f"--- HTTP RESPONSE ---\n{raw_resp[:2000]}\n\n"
            f"Evaluate if this is a confirmed vulnerability, a likely issue, or a false positive."
        )

        llm_result = llm_client.generate_json(prompt, system_instruction)
        
        # Fallback heuristic if LLM is unavailable
        if not llm_result:
            status = Finding.VerificationStatus.LIKELY
            conf = 0.75
            if payload and payload in raw_resp:
                status = Finding.VerificationStatus.CONFIRMED
                conf = 0.95
            elif not raw_resp:
                status = Finding.VerificationStatus.UNVERIFIED
                conf = 0.5
            return {
                'verification_status': status,
                'confidence_score': conf,
                'is_false_positive': False,
                'evidence_analysis': 'Heuristic analysis of reflected payloads and scanner confidence.'
            }

        status_mapping = {
            'Confirmed': Finding.VerificationStatus.CONFIRMED,
            'Likely': Finding.VerificationStatus.LIKELY,
            'Unverified': Finding.VerificationStatus.UNVERIFIED,
            'False Positive': Finding.VerificationStatus.FALSE_POSITIVE,
            'Needs Manual Review': Finding.VerificationStatus.NEEDS_MANUAL_REVIEW,
        }

        chosen_status = status_mapping.get(llm_result.get('verification_status'), Finding.VerificationStatus.LIKELY)
        conf = float(llm_result.get('confidence_score', 0.7))

        return {
            'verification_status': chosen_status,
            'confidence_score': min(max(conf, 0.0), 1.0),
            'is_false_positive': bool(llm_result.get('is_false_positive', False)),
            'evidence_analysis': llm_result.get('evidence_analysis', '')
        }

class RiskAssessmentAgent:
    """SMAI-AI-AGT-005: Evaluates business impact, exploitability, and contextual risk."""
    @staticmethod
    def assess_risk(finding: Finding, llm_client: LLMClient) -> dict:
        prompt = (
            f"Assess contextual risk for finding: {finding.title}\n"
            f"CWE: {finding.cwe_id}\n"
            f"Affected URL: {finding.affected_url}\n"
            f"Current Severity: {finding.severity}\n"
            f"Confidence: {finding.confidence_score}\n"
            "Return JSON with keys: severity (critical | high | medium | low | informational), "
            "business_impact (string), exploitability (string), priority (Immediate | High | Medium | Low)."
        )

        result = llm_client.generate_json(prompt)
        if not result:
            return {
                'severity': finding.severity,
                'business_impact': 'Potential risk to data integrity or user privacy.',
                'exploitability': 'Dependent on network access and endpoint authorization.',
                'priority': 'High' if finding.severity in ('critical', 'high') else 'Medium'
            }

        return result

class RemediationAgent:
    """SMAI-AI-AGT-006: Produces framework-tailored, copy-pasteable code patches and explanations."""
    @staticmethod
    def generate_remediation(finding: Finding, tech_stack: dict, llm_client: LLMClient) -> Remediation:
        system_instruction = (
            "You are the SecureMind AI Remediation Agent. Provide clear, developer-friendly "
            "security explanations and framework-specific code snippets to fix the reported vulnerability. "
            "Return JSON with: explanation (string), remediation_strategy (string), "
            "code_snippets (array of objects with language, file_hint, vulnerable_code, secure_code), "
            "and references (array of URLs)."
        )

        prompt = (
            f"Vulnerability: {finding.title}\n"
            f"CWE: {finding.cwe_id}\n"
            f"Affected URL/Component: {finding.affected_url} (Param: {finding.parameter})\n"
            f"Detected Tech Stack: {json.dumps(tech_stack)}\n"
            f"Provide actionable remediation guidance and secure code examples."
        )

        result = llm_client.generate_json(prompt, system_instruction)

        if not result:
            explanation = f"The application endpoint at {finding.affected_url} is susceptible to {finding.title}. Input validation and output encoding should be enforced."
            strategy = "Sanitize all external parameters, adopt parameterized APIs, and configure strict security headers."
            code_snippets = [
                {
                    'language': tech_stack.get('language', 'generic'),
                    'file_hint': 'controller/view',
                    'vulnerable_code': f"# Raw unvalidated parameter: {finding.parameter}",
                    'secure_code': "# Validate input via strict schema and escape before output"
                }
            ]
            references = [
                f"https://cwe.mitre.org/data/definitions/{finding.cwe_id.replace('CWE-', '')}.html" if finding.cwe_id else "https://owasp.org"
            ]
        else:
            explanation = result.get('explanation', '')
            strategy = result.get('remediation_strategy', '')
            code_snippets = result.get('code_snippets', [])
            references = result.get('references', [])

        remediation, created = Remediation.objects.update_or_create(
            finding=finding,
            defaults={
                'explanation': explanation,
                'remediation_strategy': strategy,
                'code_snippets': code_snippets,
                'references': references,
                'status': Remediation.Status.OPEN
            }
        )
        return remediation
