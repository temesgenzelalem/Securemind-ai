import time
import logging
from apps.orchestrator.models import AgentExecution, WorkflowState
from apps.orchestrator.services.llm_client import LLMClient
from apps.orchestrator.services.agents import (
    AuthorizationAgent,
    ReconnaissanceAgent,
    VerificationAgent,
    RiskAssessmentAgent,
    RemediationAgent,
)
from apps.findings.models import Finding
from apps.scans.models import Scan

logger = logging.getLogger(__name__)

class OrchestratorEngine:
    """
    Central AI Orchestrator (SMAI-AI-ORC-001).
    Supervises and coordinates the specialized agents across assessment stages.
    """
    @classmethod
    def process_scan_findings(cls, scan: Scan, findings: list[Finding]):
        llm_client = LLMClient()
        
        workflow_state, _ = WorkflowState.objects.get_or_create(
            scan=scan,
            defaults={'current_stage': 'reconnaissance'}
        )

        # 1. Reconnaissance Agent: Detect tech stack
        start_time = time.time()
        tech_stack = ReconnaissanceAgent.analyze_tech_stack(scan.asset, findings)
        cls._record_execution(
            scan=scan,
            agent_name=AgentExecution.AgentType.RECONNAISSANCE,
            input_payload={'asset_domain': scan.asset.domain},
            output_payload=tech_stack,
            duration=time.time() - start_time
        )
        workflow_state.current_stage = 'finding_verification'
        workflow_state.save()

        # Process each finding through Verification, Risk Assessment, and Remediation
        for finding in findings:
            # 2. Verification Agent
            start_time = time.time()
            v_res = VerificationAgent.verify_finding(finding, llm_client)
            finding.verification_status = v_res['verification_status']
            finding.confidence_score = v_res['confidence_score']
            finding.save(update_fields=['verification_status', 'confidence_score'])

            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.VERIFICATION,
                input_payload={'finding_id': str(finding.id), 'title': finding.title},
                output_payload=v_res,
                duration=time.time() - start_time
            )

            # Skip remediation generation if finding is determined to be a false positive
            if v_res.get('is_false_positive') or v_res['verification_status'] == Finding.VerificationStatus.FALSE_POSITIVE:
                continue

            # 3. Risk Assessment Agent
            start_time = time.time()
            risk_res = RiskAssessmentAgent.assess_risk(finding, llm_client)
            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.RISK_ASSESSMENT,
                input_payload={'finding_id': str(finding.id)},
                output_payload=risk_res,
                duration=time.time() - start_time
            )

            # 4. Remediation Agent
            start_time = time.time()
            rem = RemediationAgent.generate_remediation(finding, tech_stack, llm_client)
            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.REMEDIATION,
                input_payload={'finding_id': str(finding.id), 'tech_stack': tech_stack},
                output_payload={'remediation_id': str(rem.id)},
                duration=time.time() - start_time
            )

        workflow_state.current_stage = 'completed'
        workflow_state.save()

    @staticmethod
    def _record_execution(scan: Scan, agent_name: str, input_payload: dict, output_payload: dict, duration: float):
        AgentExecution.objects.create(
            scan=scan,
            agent_name=agent_name,
            status=AgentExecution.ExecutionStatus.COMPLETED,
            input_payload=input_payload,
            output_payload=output_payload,
            execution_time_seconds=round(duration, 3)
        )
