from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Report(BaseModel):
    class ReportType(models.TextChoices):
        EXECUTIVE_SUMMARY = 'executive', 'Executive Summary'
        TECHNICAL_FULL = 'technical_full', 'Full Technical Assessment Report'
        DEVELOPER_REMEDIATION = 'developer_remediation', 'Developer Remediation Guide'

    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        GENERATING = 'generating', 'Generating'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    scan = models.ForeignKey(
        'scans.Scan',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    report_type = models.CharField(
        max_length=30,
        choices=ReportType.choices,
        default=ReportType.TECHNICAL_FULL
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED
    )
    pdf_file = models.FileField(
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    metrics_summary = models.JSONField(
        default=dict,
        blank=True
    )
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Security Report'
        verbose_name_plural = 'Security Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} for Scan {self.scan_id} [{self.status}]"
