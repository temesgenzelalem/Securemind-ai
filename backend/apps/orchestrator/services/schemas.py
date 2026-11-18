from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# 1. Authorization Agent
class AuthorizationInput(BaseModel):
    asset_id: str
    target_domain: str
    requested_scan_type: str
    is_asset_verified: bool
    authorization_valid: bool
    scope_rules: List[Dict[str, Any]] = Field(default_factory=list)

class AuthorizationOutput(BaseModel):
    is_eligible_for_scan: bool
    requires_human_approval: bool
    rejection_reason: Optional[str] = None
    sanitized_scope: List[str] = Field(default_factory=list)

# 2. Reconnaissance Agent
class ReconnaissanceInput(BaseModel):
    target_domain: str
    base_url: str
    observed_headers: Dict[str, str] = Field(default_factory=dict)
    response_sample: str = ""

class ReconnaissanceOutput(BaseModel):
    detected_framework: str = "Unknown"
    detected_language: str = "Unknown"
    detected_web_server: str = "Unknown"
    identified_technologies: List[str] = Field(default_factory=list)
    security_headers_present: List[str] = Field(default_factory=list)
    security_headers_missing: List[str] = Field(default_factory=list)

# 3. Vulnerability Scanning Agent
class VulnerabilityScanningInput(BaseModel):
    target_url: str
    scan_type: str
    approved_scope: List[str] = Field(default_factory=list)
    zap_enabled: bool = True
    nuclei_enabled: bool = True

class VulnerabilityScanningOutput(BaseModel):
    scanners_dispatched: List[str] = Field(default_factory=list)
    total_raw_alerts_collected: int = 0
    scanner_statuses: Dict[str, str] = Field(default_factory=dict)
    execution_notes: str = ""

# 4. Verification Agent
class VerificationInput(BaseModel):
    finding_title: str
    vulnerability_category: str
    affected_url: str
    parameter: Optional[str] = ""
    payload_used: Optional[str] = ""
    raw_http_request: str = ""
    raw_http_response: str = ""

class VerificationOutput(BaseModel):
    verification_status: str  # Confirmed | Likely | Unverified | False Positive | Needs Manual Review
    confidence_score: float = Field(ge=0.0, le=1.0)
    is_false_positive: bool = False
    evidence_analysis: str = ""
    execution_evidence_observed: bool = False

# 5. Risk Assessment Agent
class RiskAssessmentInput(BaseModel):
    finding_title: str
    cwe_id: Optional[str] = ""
    cvss_score: Optional[float] = None
    verification_status: str
    confidence_score: float
    affected_url: str
    base_severity: str

class RiskAssessmentOutput(BaseModel):
    calculated_severity: str  # critical | high | medium | low | informational
    remediation_priority: str  # Immediate | High | Medium | Low
    business_impact: str = ""
    exploitability_assessment: str = ""
    risk_rationale: str = ""

# 6. Remediation Agent
class RemediationCodeSnippet(BaseModel):
    language: str
    file_hint: str
    vulnerable_code: str
    secure_code: str

class RemediationInput(BaseModel):
    finding_title: str
    cwe_id: Optional[str] = ""
    affected_component: str
    detected_framework: str = "Generic"
    detected_language: str = "Generic"
    vulnerability_explanation_context: str = ""

class RemediationOutput(BaseModel):
    explanation: str
    remediation_strategy: str
    code_snippets: List[RemediationCodeSnippet] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    developer_action_items: List[str] = Field(default_factory=list)
