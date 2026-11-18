from rest_framework import serializers
from apps.scans.models import Scan, ScannerExecution, ScanSchedule, AssessmentNotification
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

class ScanScheduleSerializer(serializers.ModelSerializer):
    asset_domain = serializers.CharField(source='asset.domain', read_only=True)

    class Meta:
        model = ScanSchedule
        fields = ('id', 'asset', 'asset_domain', 'organization', 'scan_type', 'frequency', 'is_active', 'last_run_at', 'next_run_at', 'created_at')
        read_only_fields = ('id', 'organization', 'last_run_at', 'created_at')

    def validate_asset(self, asset):
        if not asset.is_authorized:
            raise serializers.ValidationError("Cannot schedule scans for unverified or expired assets.")
        return asset

class AssessmentNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentNotification
        fields = ('id', 'organization', 'recipient', 'scan', 'notification_type', 'title', 'message', 'severity', 'is_read', 'details', 'created_at')
        read_only_fields = ('id', 'organization', 'recipient', 'scan', 'notification_type', 'title', 'message', 'severity', 'details', 'created_at')

