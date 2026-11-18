from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Scan(BaseModel):
    class ScanType(models.TextChoices):
        PASSIVE = 'passive', 'Passive Reconnaissance & Header Analysis'
        CONTROLLED_ACTIVE = 'controlled_active', 'Controlled Active Scan (Safe Payloads)'
        COMPREHENSIVE = 'comprehensive', 'Comprehensive Active & Template Scan'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        AUTHORIZATION_REVIEW = 'authorization_review', 'Authorization Review'
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'

    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='scans'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='scans'
    )
    scan_type = models.CharField(
        max_length=40,
        choices=ScanType.choices,
        default=ScanType.PASSIVE
    )
    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    requires_approval = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_scans'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scans'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    config_overrides = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Scan Assessment'
        verbose_name_plural = 'Scan Assessments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.scan_type} on {self.asset.domain} [{self.status}]"

class ScannerExecution(BaseModel):
    class ScannerType(models.TextChoices):
        OWASP_ZAP = 'owasp_zap', 'OWASP ZAP'
        NUCLEI = 'nuclei', 'Nuclei'

    class ExecutionStatus(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    scan = models.ForeignKey(
        Scan,
        on_delete=models.CASCADE,
        related_name='scanner_executions'
    )
    scanner_type = models.CharField(
        max_length=30,
        choices=ScannerType.choices
    )
    status = models.CharField(
        max_length=30,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.QUEUED
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    raw_output = models.JSONField(default=dict, blank=True)
    execution_stats = models.JSONField(default=dict, blank=True)
    error_log = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Scanner Execution'
        verbose_name_plural = 'Scanner Executions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.scanner_type} execution for Scan {self.scan_id} [{self.status}]"
