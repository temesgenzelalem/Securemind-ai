import json
import logging
from typing import Dict, Any
from apps.orchestrator.services.base_agent import BaseAgent
from apps.orchestrator.services.schemas import (
    AuthorizationInput, AuthorizationOutput,
    ReconnaissanceInput, ReconnaissanceOutput,
    VulnerabilityScanningInput, VulnerabilityScanningOutput,
    VerificationInput, VerificationOutput,
    RiskAssessmentInput, RiskAssessmentOutput,
    RemediationInput, RemediationOutput, RemediationCodeSnippet
)
from apps.orchestrator.services.llm_client import LLMClient, sanitize_untrusted_prompt_data

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT 1: Authorization Agent (SMAI-AI-AGT-001)
# ============================================================================
class AuthorizationAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-001"
    agent_name = "Authorization Agent"
    input_schema = AuthorizationInput
    output_schema = AuthorizationOutput

    def run(self, validated_input: AuthorizationInput) -> AuthorizationOutput:
        # Deterministic authorization checks
        if not validated_input.is_asset_verified:
            return AuthorizationOutput(
                is_eligible_for_scan=False,
                requires_human_approval=False,
                rejection_reason="Asset ownership challenge has not been verified."
            )
        if not validated_input.authorization_valid:
            return AuthorizationOutput(
                is_eligible_for_scan=False,
                requires_human_approval=False,
                rejection_reason="Asset authorization window has expired or been revoked."
            )

        # Flag active intrusive profiles for mandatory human-in-the-loop sign-off
        is_intrusive = validated_input.requested_scan_type in ('controlled_active', 'comprehensive')

        return AuthorizationOutput(
            is_eligible_for_scan=True,
            requires_human_approval=is_intrusive,
            sanitized_scope=[validated_input.target_domain]
        )

# ============================================================================
# AGENT 2: Reconnaissance Agent (SMAI-AI-AGT-002)
# ============================================================================
class ReconnaissanceAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-002"
    agent_name = "Reconnaissance Agent"
    input_schema = ReconnaissanceInput
    output_schema = ReconnaissanceOutput

    def run(self, validated_input: ReconnaissanceInput) -> ReconnaissanceOutput:
        headers = {k.lower(): v.lower() for k, v in validated_input.observed_headers.items()}
        resp_lower = validated_input.response_sample.lower()

        detected_framework = "Generic Web App"
        detected_lang = "Unknown"
        detected_server = headers.get("server", "Unknown")
        tech_list = []

        if "x-powered-by" in headers:
            powered_by = headers["x-powered-by"]
            tech_list.append(f"X-Powered-By: {powered_by}")
            if "next.js" in powered_by or "/_next/" in resp_lower:
                detected_framework = "Next.js"
                detected_lang = "TypeScript/JavaScript"
            elif "php" in powered_by:
                detected_lang = "PHP"
                detected_framework = "Laravel/PHP" if "laravel" in resp_lower else "PHP"

        if "csrftoken" in resp_lower or "django" in resp_lower:
            detected_framework = "Django"
            detected_lang = "Python"
            tech_list.append("Django CSRF Framework")

        # Security Headers Audit
        standard_sec_headers = [
            "content-security-policy",
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy"
        ]
        present = [h for h in standard_sec_headers if h in headers]
        missing = [h for h in standard_sec_headers if h not in headers]

        return ReconnaissanceOutput(
            detected_framework=detected_framework,
            detected_language=detected_lang,
            detected_web_server=detected_server,
            identified_technologies=tech_list,
            security_headers_present=present,
            security_headers_missing=missing
        )

# ============================================================================
# AGENT 3: Vulnerability Scanning Agent (SMAI-AI-AGT-003)
# ============================================================================
class VulnerabilityScanningAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-003"
    agent_name = "Vulnerability Scanning Agent"
    input_schema = VulnerabilityScanningInput
    output_schema = VulnerabilityScanningOutput

    def run(self, validated_input: VulnerabilityScanningInput) -> VulnerabilityScanningOutput:
        dispatched = []
        statuses = {}

        if validated_input.zap_enabled:
            dispatched.append("OWASP ZAP")
            statuses["zap"] = "Executed"
        if validated_input.nuclei_enabled:
            dispatched.append("Nuclei")
            statuses["nuclei"] = "Executed"

        return VulnerabilityScanningOutput(
            scanners_dispatched=dispatched,
            total_raw_alerts_collected=0,
            scanner_statuses=statuses,
            execution_notes=f"Dispatched {len(dispatched)} engines against {validated_input.target_url}."
        )

# ============================================================================
# AGENT 4: Verification Agent (SMAI-AI-AGT-004)
# ============================================================================
class VerificationAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-004"
    agent_name = "Verification Agent"
    input_schema = VerificationInput
    output_schema = VerificationOutput

    def run(self, validated_input: VerificationInput) -> VerificationOutput:
        payload = validated_input.payload_used or ""
        resp = validated_input.raw_http_response or ""

        # Deterministic Heuristic Baseline
        is_false_pos = False
        evidence_observed = False
        status = "unverified"
        confidence = 0.5

        if payload and payload in resp:
            evidence_observed = True
            status = "confirmed"
            confidence = 0.95
        elif not resp:
            status = "unverified"
            confidence = 0.4
        else:
            status = "likely"
            confidence = 0.7

        # LLM Reasoning if provider is active
        if self.llm_client and self.llm_client.is_ai_enabled:
            safe_req = sanitize_untrusted_prompt_data(validated_input.raw_http_request)
            safe_resp = sanitize_untrusted_prompt_data(resp)
            prompt = (
                f"Finding: {validated_input.finding_title}\n"
                f"Category: {validated_input.vulnerability_category}\n"
                f"URL: {validated_input.affected_url}\n"
                f"Payload: {payload}\n"
                f"Request: {safe_req}\n"
                f"Response: {safe_resp}\n"
                "Evaluate whether this is confirmed, likely, unverified, or false_positive. Return JSON."
            )
            llm_res = self.llm_client.generate_json(prompt)
            if llm_res and "verification_status" in llm_res:
                status = str(llm_res.get("verification_status", status)).lower().replace(" ", "_")
                confidence = float(llm_res.get("confidence_score", confidence))
                is_false_pos = bool(llm_res.get("is_false_positive", False))

        return VerificationOutput(
            verification_status=status.lower(),
            confidence_score=min(max(confidence, 0.0), 1.0),
            is_false_positive=is_false_pos,
            evidence_analysis="Technical evidence evaluation completed.",
            execution_evidence_observed=evidence_observed
        )

# ============================================================================
# AGENT 5: Risk Assessment Agent (SMAI-AI-AGT-005)
# ============================================================================
class RiskAssessmentAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-005"
    agent_name = "Risk Assessment Agent"
    input_schema = RiskAssessmentInput
    output_schema = RiskAssessmentOutput

    def run(self, validated_input: RiskAssessmentInput) -> RiskAssessmentOutput:
        sev = validated_input.base_severity.lower()
        priority_map = {
            "critical": "Immediate",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "informational": "Low"
        }
        priority = priority_map.get(sev, "Medium")

        return RiskAssessmentOutput(
            calculated_severity=sev,
            remediation_priority=priority,
            business_impact="Evaluated based on exposure of affected endpoint and CVSS metric.",
            exploitability_assessment="Exploitable based on verified technical payload evidence.",
            risk_rationale=f"Prioritized as {priority} due to {sev} severity classification."
        )

# ============================================================================
# AGENT 6: Remediation Agent (SMAI-AI-AGT-006)
# ============================================================================
class RemediationAgent(BaseAgent):
    agent_id = "SMAI-AI-AGT-006"
    agent_name = "Remediation Agent"
    input_schema = RemediationInput
    output_schema = RemediationOutput

    def run(self, validated_input: RemediationInput) -> RemediationOutput:
        fw = validated_input.detected_framework
        title = validated_input.finding_title

        explanation = f"The application at {validated_input.affected_component} contains {title}."
        strategy = f"Implement input validation and safe contextual encoding tailored to {fw}."
        snippets = [
            RemediationCodeSnippet(
                language=validated_input.detected_language,
                file_hint="views / controller",
                vulnerable_code="# Raw parameter reflection without sanitization",
                secure_code="# Validate input with strict schema and escape output context"
            )
        ]
        references = [
            f"https://cwe.mitre.org/data/definitions/{validated_input.cwe_id.replace('CWE-', '')}.html" if validated_input.cwe_id else "https://owasp.org"
        ]

        # LLM-enhanced generation if provider active
        if self.llm_client and self.llm_client.is_ai_enabled:
            prompt = (
                f"Vulnerability: {title}\n"
                f"Framework: {fw}\n"
                f"Component: {validated_input.affected_component}\n"
                "Provide actionable remediation guidance and secure code examples in JSON."
            )
            res = self.llm_client.generate_json(prompt)
            if res and "explanation" in res:
                explanation = res.get("explanation", explanation)
                strategy = res.get("remediation_strategy", strategy)

        return RemediationOutput(
            explanation=explanation,
            remediation_strategy=strategy,
            code_snippets=snippets,
            references=references,
            developer_action_items=["Review code diff", "Test in staging environment", "Deploy patch"]
        )
