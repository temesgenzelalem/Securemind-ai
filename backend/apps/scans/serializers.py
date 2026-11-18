from rest_framework import serializers
from apps.scans.models import Scan, ScannerExecution
from apps.assets.models import Asset

class ScannerExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScannerExecution
        fields = ('id', 'scanner_type', 'status', 'started_at', 'completed_at', 'raw_output', 'execution_stats', 'error_log')

class ScanSerializer(serializers.ModelSerializer):
    asset_domain = serializers.CharField(source='asset.domain', read_only=True)
    scanner_executions = ScannerExecutionSerializer(many=True, read_only=True)
    findings_count = serializers.IntegerField(source='findings.count', read_only=True)

    class Meta:
        model = Scan
        fields = (
            'id', 'asset', 'asset_domain', 'organization', 'scan_type',
            'status', 'requires_approval', 'is_approved', 'started_at',
            'completed_at', 'findings_count', 'scanner_executions',
            'error_message', 'created_at'
        )
        read_only_fields = ('id', 'organization', 'status', 'started_at', 'completed_at', 'findings_count', 'created_at')

class CreateScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = ('asset', 'scan_type', 'config_overrides')

    def validate_asset(self, asset):
        if not asset.is_authorized:
            raise serializers.ValidationError("Target asset has not verified ownership or authorization has expired.")
        return asset
