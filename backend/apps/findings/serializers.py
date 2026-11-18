from rest_framework import serializers
from apps.findings.models import Finding, Evidence

class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ('id', 'evidence_type', 'raw_http_request', 'raw_http_response', 'payload_used', 'extracted_proof', 'verification_notes', 'created_at')

class FindingSerializer(serializers.ModelSerializer):
    evidences = EvidenceSerializer(many=True, read_only=True)
    remediation_id = serializers.UUIDField(source='remediation.id', read_only=True)
    remediation_status = serializers.CharField(source='remediation.status', read_only=True)

    class Meta:
        model = Finding
        fields = (
            'id', 'scan', 'asset', 'organization', 'title', 'description',
            'vulnerability_category', 'cwe_id', 'cvss_vector', 'cvss_score',
            'severity', 'verification_status', 'confidence_score',
            'source_scanner', 'affected_url', 'http_method', 'parameter',
            'remediation_id', 'remediation_status', 'evidences',
            'first_detected_at', 'last_observed_at', 'created_at'
        )
        read_only_fields = ('id', 'scan', 'asset', 'organization', 'fingerprint', 'created_at')
