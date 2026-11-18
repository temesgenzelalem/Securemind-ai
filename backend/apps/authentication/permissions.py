from rest_framework import permissions
from apps.authentication.models import User
from apps.organizations.models import Membership

class IsPlatformAdmin(permissions.BasePermission):
    """Allows access only to platform super administrators."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.PLATFORM_ADMIN or request.user.is_superuser)
        )

class IsOrgAdmin(permissions.BasePermission):
    """Allows access to organization administrators or platform admins."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == User.Role.PLATFORM_ADMIN or request.user.is_superuser:
            return True
        if request.user.role == User.Role.ORG_ADMIN:
            return True
        if request.user.current_organization_id:
            return Membership.objects.filter(
                user=request.user,
                organization_id=request.user.current_organization_id,
                role=Membership.OrgRole.ADMIN,
                is_active=True
            ).exists()
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.PLATFORM_ADMIN or request.user.is_superuser:
            return True
        # Check org-level membership role
        org = getattr(obj, 'organization', obj)
        return Membership.objects.filter(
            user=request.user,
            organization=org,
            role=Membership.OrgRole.ADMIN,
            is_active=True
        ).exists()

class IsSecurityAnalystOrAbove(permissions.BasePermission):
    """Allows access to Security Analysts, Org Admins, and Platform Admins."""
    ALLOWED_ROLES = {
        User.Role.PLATFORM_ADMIN,
        User.Role.ORG_ADMIN,
        User.Role.SECURITY_ANALYST,
    }

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in self.ALLOWED_ROLES

class IsDeveloperOrAbove(permissions.BasePermission):
    """Allows access to Developers, Analysts, Org Admins, and Platform Admins (read/write findings)."""
    ALLOWED_ROLES = {
        User.Role.PLATFORM_ADMIN,
        User.Role.ORG_ADMIN,
        User.Role.SECURITY_ANALYST,
        User.Role.DEVELOPER,
    }

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        return request.user.role in self.ALLOWED_ROLES

class TenantObjectPermission(permissions.BasePermission):
    """
    Ensures users can only access objects belonging to an organization they are a member of.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.PLATFORM_ADMIN or request.user.is_superuser:
            return True

        target_org = getattr(obj, 'organization', None)
        if target_org is None and hasattr(obj, 'project'):
            target_org = obj.project.organization

        if target_org is None:
            return True

        return Membership.objects.filter(
            user=request.user,
            organization=target_org,
            is_active=True
        ).exists()
