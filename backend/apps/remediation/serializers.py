from rest_framework import serializers
from apps.remediation.models import Remediation

class RemediationSerializer(serializers.ModelSerializer):
    finding_title = serializers.CharField(source='finding.title', read_only=True)
    finding_severity = serializers.CharField(source='finding.severity', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)

    class Meta:
        model = Remediation
        fields = (
            'id', 'finding', 'finding_title', 'finding_severity', 'status',
            'explanation', 'remediation_strategy', 'code_snippets', 'references',
            'assigned_to', 'assigned_to_email', 'resolved_by', 'resolved_at',
            'developer_notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'finding', 'explanation', 'remediation_strategy', 'code_snippets', 'references', 'created_at')

class UpdateRemediationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remediation
        fields = ('status', 'developer_notes', 'assigned_to')
