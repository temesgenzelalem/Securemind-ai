from django.db import models
from apps.core.models import BaseModel

class AgentExecution(BaseModel):
    class AgentType(models.TextChoices):
        CENTRAL_ORCHESTRATOR = 'central_orchestrator', 'Central AI Orchestrator'
        AUTHORIZATION = 'authorization', 'Authorization Agent'
        RECONNAISSANCE = 'reconnaissance', 'Reconnaissance Agent'
        VULNERABILITY_SCANNING = 'vulnerability_scanning', 'Vulnerability Scanning Agent'
        VERIFICATION = 'verification', 'Verification Agent'
        RISK_ASSESSMENT = 'risk_assessment', 'Risk Assessment Agent'
        REMEDIATION = 'remediation', 'Remediation Agent'

    class ExecutionStatus(models.TextChoices):
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    scan = models.ForeignKey(
        'scans.Scan',
        on_delete=models.CASCADE,
        related_name='agent_executions'
    )
    agent_name = models.CharField(
        max_length=40,
        choices=AgentType.choices
    )
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.RUNNING
    )
    input_payload = models.JSONField(default=dict, blank=True)
    output_payload = models.JSONField(default=dict, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    execution_time_seconds = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'AI Agent Execution'
        verbose_name_plural = 'AI Agent Executions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.agent_name} for Scan {self.scan_id} [{self.status}]"

class WorkflowState(BaseModel):
    scan = models.OneToOneField(
        'scans.Scan',
        on_delete=models.CASCADE,
        related_name='workflow_state'
    )
    current_stage = models.CharField(max_length=60, default='authorization_check')
    stage_history = models.JSONField(default=list, blank=True)
    is_halted = models.BooleanField(default=False)
    halt_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Assessment Workflow State'
        verbose_name_plural = 'Assessment Workflow States'

    def __str__(self):
        return f"Workflow for Scan {self.scan_id} (Stage: {self.current_stage})"
