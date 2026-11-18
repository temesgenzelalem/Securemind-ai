from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel

class Finding(BaseModel):
    class Severity(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'
        INFORMATIONAL = 'informational', 'Informational'

    class VerificationStatus(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        LIKELY = 'likely', 'Likely'
        UNVERIFIED = 'unverified', 'Unverified'
        FALSE_POSITIVE = 'false_positive', 'False Positive'
        NEEDS_MANUAL_REVIEW = 'needs_manual_review', 'Needs Manual Review'

    scan = models.ForeignKey(
        'scans.Scan',
        on_delete=models.CASCADE,
        related_name='findings'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='findings'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='findings'
    )
    title = models.CharField(max_length=300, db_index=True)
    description = models.TextField()
    vulnerability_category = models.CharField(max_length=150, blank=True)
    cwe_id = models.CharField(max_length=50, blank=True, help_text="e.g. CWE-89, CWE-79")
    cvss_vector = models.CharField(max_length=100, blank=True)
    cvss_score = models.FloatField(null=True, blank=True)
    
    severity = models.CharField(
        max_length=30,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        db_index=True
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
        db_index=True
    )
    confidence_score = models.FloatField(
        default=0.5,
        help_text="Confidence rating between 0.0 and 1.0 assigned by Verification Agent"
    )
    source_scanner = models.CharField(max_length=50, default='scanner')
    
    affected_url = models.URLField(max_length=1000)
    http_method = models.CharField(max_length=15, default='GET')
    parameter = models.CharField(max_length=200, blank=True)

    fingerprint = models.CharField(
        max_length=128,
        db_index=True,
        blank=True,
        help_text="Hash of title + affected_url + parameter for deduplication"
    )

    first_detected_at = models.DateTimeField(default=timezone.now)
    last_observed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Vulnerability Finding'
        verbose_name_plural = 'Vulnerability Findings'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} ({self.verification_status})"

class Evidence(BaseModel):
    class EvidenceType(models.TextChoices):
        HTTP_TRAFFIC = 'http_traffic', 'Full HTTP Traffic'
        RESPONSE_REFLECTION = 'response_reflection', 'Payload Reflection in DOM'
        HEADER_MISCONFIGURATION = 'header_misconfiguration', 'Security Header Misconfiguration'
        TIMING_DIFFERENTIAL = 'timing_differential', 'Time-based Response Differential'

    finding = models.ForeignKey(
        Finding,
        on_delete=models.CASCADE,
        related_name='evidences'
    )
    evidence_type = models.CharField(
        max_length=50,
        choices=EvidenceType.choices,
        default=EvidenceType.HTTP_TRAFFIC
    )
    raw_http_request = models.TextField(blank=True)
    raw_http_response = models.TextField(blank=True)
    payload_used = models.TextField(blank=True)
    extracted_proof = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Finding Evidence'
        verbose_name_plural = 'Finding Evidences'

    def __str__(self):
        return f"{self.evidence_type} evidence for Finding {self.finding_id}"
