from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Remediation(BaseModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FIXED = 'fixed', 'Fixed'
        ACCEPTED_RISK = 'accepted_risk', 'Accepted Risk'
        FALSE_POSITIVE = 'false_positive', 'Marked as False Positive'
        REOPENED = 'reopened', 'Reopened'

    finding = models.OneToOneField(
        'findings.Finding',
        on_delete=models.CASCADE,
        related_name='remediation'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True
    )
    explanation = models.TextField(
        help_text="Developer-friendly explanation of the vulnerability"
    )
    remediation_strategy = models.TextField(
        help_text="High-level architectural and implementation approach"
    )
    code_snippets = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of language/framework specific remediation snippets"
    )
    references = models.JSONField(
        default=list,
        blank=True,
        help_text="List of official references, OWASP links, and documentation"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_remediations'
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_remediations'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    developer_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Remediation Record'
        verbose_name_plural = 'Remediation Records'
        ordering = ['-created_at']

    def __str__(self):
        return f"Remediation for Finding {self.finding_id} [{self.status}]"
