import secrets
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel

class Asset(BaseModel):
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        VERIFIED = 'verified', 'Verified'
        FAILED = 'failed', 'Verification Failed'
        EXPIRED = 'expired', 'Authorization Expired'

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='assets'
    )
    project = models.ForeignKey(
        'organizations.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=255, db_index=True)
    base_url = models.URLField(max_length=500)
    
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    authorization_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        unique_together = ('organization', 'domain')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.domain}) [{self.verification_status}]"

    @property
    def is_authorized(self):
        if self.verification_status != self.VerificationStatus.VERIFIED:
            return False
        if self.authorization_expires_at and self.authorization_expires_at < timezone.now():
            return False
        return True

class AuthorizationChallenge(BaseModel):
    class ChallengeType(models.TextChoices):
        DNS_TXT = 'dns_txt', 'DNS TXT Record'
        HTTP_TOKEN = 'http_token', 'HTTP Well-Known Token File'

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='challenges'
    )
    challenge_type = models.CharField(
        max_length=30,
        choices=ChallengeType.choices,
        default=ChallengeType.DNS_TXT
    )
    token = models.CharField(max_length=128, default=secrets.token_urlsafe)
    verification_path = models.CharField(
        max_length=255,
        default='/.well-known/securemind-challenge.txt'
    )
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    last_attempt_error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Authorization Challenge'
        verbose_name_plural = 'Authorization Challenges'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.challenge_type} for {self.asset.domain} (Verified: {self.is_verified})"

class ScopeRule(BaseModel):
    class RuleType(models.TextChoices):
        INCLUDE = 'include', 'Permitted / In-Scope'
        EXCLUDE = 'exclude', 'Excluded / Out-of-Scope'

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='scope_rules'
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        default=RuleType.INCLUDE
    )
    pattern = models.CharField(
        max_length=500,
        help_text="Path or regex pattern, e.g. '/api/*' or '/admin/logout'"
    )
    port = models.PositiveIntegerField(null=True, blank=True, help_text="Optional port restriction")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Scope Rule'
        verbose_name_plural = 'Scope Rules'

    def __str__(self):
        return f"[{self.rule_type.upper()}] {self.pattern} for {self.asset.domain}"
