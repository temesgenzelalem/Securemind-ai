from rest_framework import serializers
from apps.reports.models import Report

class ReportSerializer(serializers.ModelSerializer):
    scan_target = serializers.CharField(source='scan.asset.domain', read_only=True)
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'scan', 'scan_target', 'organization', 'generated_by', 'generated_by_email', 'report_type', 'status', 'pdf_file', 'metrics_summary', 'error_message', 'created_at')
        read_only_fields = ('id', 'organization', 'generated_by', 'status', 'pdf_file', 'metrics_summary', 'error_message', 'created_at')

class GenerateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('scan', 'report_type')
