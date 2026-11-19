from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from apps.assets.models import Asset, AuthorizationChallenge, ScopeRule
from apps.assets.serializers import (
    AssetSerializer,
    AuthorizationChallengeSerializer,
    ScopeRuleSerializer,
    CreateChallengeSerializer
)
from apps.assets.services.verifier import AssetVerificationService
from apps.authentication.permissions import TenantObjectPermission, IsSecurityAnalystOrAbove
from apps.audit.models import AuditLog

class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'challenge', 'verify', 'scope_rules'):
            return [permissions.IsAuthenticated(), IsSecurityAnalystOrAbove(), TenantObjectPermission()]
        return [permissions.IsAuthenticated(), TenantObjectPermission()]

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return Asset.objects.none()

        qs = Asset.objects.filter(is_active=True).prefetch_related('challenges', 'scope_rules')
        if not user.is_superuser:
            qs = qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        org = user.current_organization
        asset = serializer.save(organization=org)

        # Automatically create initial DNS TXT verification challenge valid for 7 days
        challenge = AuthorizationChallenge.objects.create(
            asset=asset,
            challenge_type=AuthorizationChallenge.ChallengeType.DNS_TXT,
            expires_at=timezone.now() + timedelta(days=7)
        )

        AuditLog.objects.create(
            organization=org,
            actor=user,
            action='asset_registered',
            target_type='Asset',
            target_id=str(asset.id),
            details={'domain': asset.domain, 'base_url': asset.base_url}
        )

    @action(detail=True, methods=['post'], serializer_class=CreateChallengeSerializer)
    def challenge(self, request, pk=None):
        """Generate a new DNS or HTTP ownership verification challenge."""
        asset = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        challenge_type = serializer.validated_data['challenge_type']

        challenge = AuthorizationChallenge.objects.create(
            asset=asset,
            challenge_type=challenge_type,
            expires_at=timezone.now() + timedelta(days=7)
        )

        AuditLog.objects.create(
            organization=asset.organization,
            actor=request.user,
            action='challenge_created',
            target_type='AuthorizationChallenge',
            target_id=str(challenge.id),
            details={'type': challenge_type, 'domain': asset.domain}
        )

        return Response(AuthorizationChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Trigger immediate DNS TXT or HTTP verification check."""
        asset = self.get_object()
        challenge_id = request.data.get('challenge_id')

        if challenge_id:
            challenge = asset.challenges.filter(id=challenge_id).first()
        else:
            challenge = asset.challenges.order_by('-created_at').first()

        if not challenge:
            return Response({'error': 'No verification challenge found for this asset.'}, status=status.HTTP_400_BAD_REQUEST)

        success, message = AssetVerificationService.verify_challenge(challenge)

        AuditLog.objects.create(
            organization=asset.organization,
            actor=request.user,
            action='challenge_verified' if success else 'challenge_verification_failed',
            target_type='Asset',
            target_id=str(asset.id),
            details={'success': success, 'message': message}
        )

        return Response({
            'verified': success,
            'message': message,
            'asset': AssetSerializer(asset).data,
            'challenge': AuthorizationChallengeSerializer(challenge).data
        }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def scope_rules(self, request, pk=None):
        asset = self.get_object()
        if request.method == 'GET':
            rules = asset.scope_rules.filter(is_active=True)
            return Response(ScopeRuleSerializer(rules, many=True).data)

        # POST: Add new scope rule
        serializer = ScopeRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule = serializer.save(asset=asset)
        return Response(ScopeRuleSerializer(rule).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Assessment history and finding progression for an asset (FR-MON-004)."""
        asset = self.get_object()
        from apps.scans.services.comparison import ScanComparisonService
        history_data = ScanComparisonService.get_asset_history(str(asset.id))
        return Response({
            'asset_id': str(asset.id),
            'domain': asset.domain,
            'total_scans': len(history_data),
            'history': history_data
        }, status=status.HTTP_200_OK)

class ScopeRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ScopeRuleSerializer
    permission_classes = (permissions.IsAuthenticated, TenantObjectPermission)

    def get_queryset(self):
        user = self.request.user
        org = user.current_organization
        if not org and not user.is_superuser:
            return ScopeRule.objects.none()
        return ScopeRule.objects.filter(asset__organization=org, is_active=True)
