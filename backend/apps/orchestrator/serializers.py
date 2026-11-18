from rest_framework import serializers
from apps.orchestrator.models import AgentExecution, WorkflowState

class AgentExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentExecution
        fields = (
            'id', 'scan', 'agent_name', 'status', 'input_payload',
            'output_payload', 'model_used', 'tokens_used',
            'execution_time_seconds', 'error_message', 'created_at'
        )
        read_only_fields = fields

class WorkflowStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowState
        fields = ('id', 'scan', 'current_stage', 'stage_history', 'is_halted', 'halt_reason', 'created_at')
        read_only_fields = fields
