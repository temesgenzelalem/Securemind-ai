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

        recon_agent = ReconnaissanceAgent(llm_client)
        verify_agent = VerificationAgent(llm_client)
        risk_agent = RiskAssessmentAgent(llm_client)
        remed_agent = RemediationAgent(llm_client)

        # 1. Reconnaissance Agent: Detect tech stack
        start_time = time.time()
        recon_input = {
            'target_domain': scan.asset.domain,
            'base_url': scan.asset.base_url,
            'observed_headers': {},
            'response_sample': findings[0].evidences.first().raw_http_response if (findings and findings[0].evidences.exists()) else ""
        }
        tech_stack = recon_agent.execute(recon_input)
        cls._record_execution(
            scan=scan,
            agent_name=AgentExecution.AgentType.RECONNAISSANCE,
            input_payload=recon_input,
            output_payload=tech_stack,
            duration=time.time() - start_time
        )
        workflow_state.current_stage = 'finding_verification'
        workflow_state.save()

        # Process each finding through Verification, Risk Assessment, and Remediation
        for finding in findings:
            evidence = finding.evidences.first()

            # 2. Verification Agent
            start_time = time.time()
            v_input = {
                'finding_title': finding.title,
                'vulnerability_category': finding.vulnerability_category or 'General',
                'affected_url': finding.affected_url,
                'parameter': finding.parameter,
                'payload_used': evidence.payload_used if evidence else '',
                'raw_http_request': evidence.raw_http_request if evidence else '',
                'raw_http_response': evidence.raw_http_response if evidence else '',
            }
            v_res = verify_agent.execute(v_input)
            finding.verification_status = v_res['verification_status']
            finding.confidence_score = v_res['confidence_score']
            finding.save(update_fields=['verification_status', 'confidence_score'])

            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.VERIFICATION,
                input_payload=v_input,
                output_payload=v_res,
                duration=time.time() - start_time
            )

            # Skip remediation generation if finding is determined to be a false positive
            if v_res.get('is_false_positive') or v_res['verification_status'] == Finding.VerificationStatus.FALSE_POSITIVE:
                continue

            # 3. Risk Assessment Agent
            start_time = time.time()
            risk_input = {
                'finding_title': finding.title,
                'cwe_id': finding.cwe_id,
                'cvss_score': finding.cvss_score,
                'verification_status': finding.verification_status,
                'confidence_score': finding.confidence_score,
                'affected_url': finding.affected_url,
                'base_severity': finding.severity,
            }
            risk_res = risk_agent.execute(risk_input)
            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.RISK_ASSESSMENT,
                input_payload=risk_input,
                output_payload=risk_res,
                duration=time.time() - start_time
            )

            # 4. Remediation Agent
            start_time = time.time()
            rem_input = {
                'finding_title': finding.title,
                'cwe_id': finding.cwe_id,
                'affected_component': finding.affected_url,
                'detected_framework': tech_stack.get('detected_framework', 'Generic'),
                'detected_language': tech_stack.get('detected_language', 'Generic'),
            }
            rem_res = remed_agent.execute(rem_input)
            
            from apps.remediation.models import Remediation
            Remediation.objects.update_or_create(
                finding=finding,
                defaults={
                    'explanation': rem_res['explanation'],
                    'remediation_strategy': rem_res['remediation_strategy'],
                    'code_snippets': rem_res['code_snippets'],
                    'references': rem_res['references'],
                    'status': Remediation.Status.OPEN
                }
            )

            cls._record_execution(
                scan=scan,
                agent_name=AgentExecution.AgentType.REMEDIATION,
                input_payload=rem_input,
                output_payload=rem_res,
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
