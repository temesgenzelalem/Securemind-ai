from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.text import slugify
from apps.organizations.models import Organization, Project, Membership
from apps.organizations.serializers import (
    OrganizationSerializer,
    ProjectSerializer,
    MembershipSerializer,
    InviteMemberSerializer
)
from apps.authentication.models import User
from apps.authentication.permissions import IsOrgAdmin, TenantObjectPermission
from apps.audit.models import AuditLog

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy', 'members'):
            return [permissions.IsAuthenticated(), IsOrgAdmin(), TenantObjectPermission()]
        return [permissions.IsAuthenticated(), TenantObjectPermission()]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.PLATFORM_ADMIN or user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(memberships__user=user, memberships__is_active=True).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        name = serializer.validated_data.get('name')
        base_slug = slugify(name)
        slug = f"{base_slug}-{str(user.id)[:6]}"
        
        org = serializer.save(slug=slug, created_by=user)
        
        # Creator becomes Org Admin
        Membership.objects.create(
            user=user,
            organization=org,
            role=Membership.OrgRole.ADMIN
        )

        AuditLog.objects.create(
            organization=org,
            actor=user,
            action='organization_created',
            target_type='Organization',
            target_id=str(org.id),
            details={'name': org.name}
        )

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated, IsOrgAdmin])
    def members(self, request, pk=None):
        org = self.get_object()
        
        if request.method == 'GET':
            memberships = org.memberships.select_related('user').filter(is_active=True)
            serializer = MembershipSerializer(memberships, many=True)
            return Response(serializer.data)

        # POST: Invite / Add member
        invite_serializer = InviteMemberSerializer(data=request.data)
        invite_serializer.is_valid(raise_exception=True)
        email = invite_serializer.validated_data['email']
        role = invite_serializer.validated_data['role']

        target_user = User.objects.filter(email=email).first()
        if not target_user:
            return Response({'error': f"User with email '{email}' does not exist on the platform."}, status=status.HTTP_404_NOT_FOUND)

        membership, created = Membership.objects.get_or_create(
            user=target_user,
            organization=org,
            defaults={'role': role, 'is_active': True}
        )

        if not created:
            membership.role = role
            membership.is_active = True
            membership.save()

        AuditLog.objects.create(
            organization=org,
            actor=request.user,
            action='member_added',
            target_type='User',
            target_id=str(target_user.id),
            details={'email': email, 'role': role}
        )

        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Project.objects.none()
        
        qs = Project.objects.filter(is_active=True)
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        org = self.request.user.current_organization
        serializer.save(organization=org)
