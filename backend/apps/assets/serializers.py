from rest_framework import serializers
from urllib.parse import urlparse
from django.utils import timezone
from datetime import timedelta
from apps.assets.models import Asset, AuthorizationChallenge, ScopeRule
from apps.assets.services.verifier import TargetSafetyValidator, SecurityScopeError

class ScopeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeRule
        fields = ('id', 'asset', 'rule_type', 'pattern', 'port', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

class AuthorizationChallengeSerializer(serializers.ModelSerializer):
    dns_record_name = serializers.SerializerMethodField()
    expected_dns_value = serializers.SerializerMethodField()
    http_file_url = serializers.SerializerMethodField()

    class Meta:
        model = AuthorizationChallenge
        fields = (
            'id', 'asset', 'challenge_type', 'token', 'verification_path',
            'is_verified', 'verified_at', 'expires_at', 'last_attempt_at',
            'last_attempt_error', 'dns_record_name', 'expected_dns_value',
            'http_file_url', 'created_at'
        )
        read_only_fields = ('id', 'token', 'is_verified', 'verified_at', 'expires_at', 'last_attempt_at', 'last_attempt_error', 'created_at')

    def get_dns_record_name(self, obj):
        return f"_securemind-challenge.{obj.asset.domain}"

    def get_expected_dns_value(self, obj):
        return f"securemind-verify={obj.token}"

    def get_http_file_url(self, obj):
        return f"{obj.asset.base_url.rstrip('/')}{obj.verification_path}"

class AssetSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(required=False)
    is_authorized = serializers.BooleanField(read_only=True)
    challenges = AuthorizationChallengeSerializer(many=True, read_only=True)
    scope_rules = ScopeRuleSerializer(many=True, read_only=True)

    class Meta:
        model = Asset
        fields = (
            'id', 'organization', 'project', 'name', 'domain', 'base_url',
            'verification_status', 'is_authorized', 'verified_at',
            'authorization_expires_at', 'is_active', 'challenges',
            'scope_rules', 'created_at'
        )
        read_only_fields = (
            'id', 'organization', 'verification_status', 'is_authorized',
            'verified_at', 'authorization_expires_at', 'created_at'
        )

    def validate_base_url(self, value):
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            raise serializers.ValidationError("Base URL must start with http:// or https://")
        if not parsed.netloc:
            raise serializers.ValidationError("Base URL must include a valid hostname.")
        return value

    def validate(self, attrs):
        base_url = attrs.get('base_url')
        domain = attrs.get('domain', '').strip().lower()

        # Normalize domain from base_url if not explicitly provided
        if not domain and base_url:
            domain = urlparse(base_url).netloc.split(':')[0].lower()
            attrs['domain'] = domain

        # Run deterministic SSRF pre-check on registered domain
        try:
            TargetSafetyValidator.validate_target_safety(domain)
        except SecurityScopeError as e:
            raise serializers.ValidationError({"domain": str(e)})

        return attrs

class CreateChallengeSerializer(serializers.Serializer):
    challenge_type = serializers.ChoiceField(
        choices=AuthorizationChallenge.ChallengeType.choices,
        default=AuthorizationChallenge.ChallengeType.DNS_TXT
    )
