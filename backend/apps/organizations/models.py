from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Organization(BaseModel):
    class PlanType(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Professional'
        ENTERPRISE = 'enterprise', 'Enterprise'

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True)
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.FREE
    )
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_organizations'
    )

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']

    def __str__(self):
        return self.name

class Project(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        unique_together = ('organization', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.organization.name} / {self.name}"

class Membership(BaseModel):
    class OrgRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        SECURITY_ANALYST = 'analyst', 'Security Analyst'
        DEVELOPER = 'developer', 'Developer'
        VIEWER = 'viewer', 'Viewer'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=30,
        choices=OrgRole.choices,
        default=OrgRole.DEVELOPER
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.email} in {self.organization.name} ({self.role})"
