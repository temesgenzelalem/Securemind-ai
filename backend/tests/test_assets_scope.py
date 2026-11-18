import os
import django
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['USE_SQLITE'] = 'True'
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership
from apps.assets.models import Asset, AuthorizationChallenge, ScopeRule
from apps.assets.services.verifier import AssetVerificationService, TargetSafetyValidator, SecurityScopeError

class AssetAndScopeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='security@example.com',
            password='StrongPassword123!',
            role=User.Role.ORG_ADMIN
        )
        self.org = Organization.objects.create(name='Security Team Org', slug='security-team')
        Membership.objects.create(user=self.user, organization=self.org, role=Membership.OrgRole.ADMIN)
        self.user.current_organization = self.org
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_asset_registration_and_challenge_generation(self):
        payload = {
            'name': 'Production Web App',
            'base_url': 'https://example.com'
        }
        with patch('apps.assets.serializers.TargetSafetyValidator.validate_target_safety'), \
             patch('apps.assets.services.verifier.TargetSafetyValidator.validate_target_safety'):
            response = self.client.post('/api/v1/assets/', payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['domain'], 'example.com')
            self.assertEqual(response.data['verification_status'], Asset.VerificationStatus.PENDING)
            self.assertFalse(response.data['is_authorized'])

            # Verify challenge created automatically
            asset_id = response.data['id']
            challenges = AuthorizationChallenge.objects.filter(asset_id=asset_id)
            self.assertTrue(challenges.exists())
            self.assertEqual(challenges.first().challenge_type, AuthorizationChallenge.ChallengeType.DNS_TXT)

    def test_dns_txt_verification_success(self):
        asset = Asset.objects.create(
            organization=self.org,
            name='DNS App',
            domain='dns.example.com',
            base_url='https://dns.example.com',
            verification_status=Asset.VerificationStatus.PENDING
        )
        challenge = AuthorizationChallenge.objects.create(
            asset=asset,
            challenge_type=AuthorizationChallenge.ChallengeType.DNS_TXT,
            token='test-dns-token-12345',
            expires_at=timezone.now() + timedelta(days=7)
        )

        # Mock dns.resolver.resolve returning the expected token
        mock_rdata = MagicMock()
        mock_rdata.strings = [b'securemind-verify=test-dns-token-12345']
        
        with patch('apps.assets.services.verifier.TargetSafetyValidator.validate_target_safety'), \
             patch('apps.assets.services.verifier.dns.resolver.resolve', return_value=[mock_rdata]):
            
            success, message = AssetVerificationService.verify_challenge(challenge)
            self.assertTrue(success)
            self.assertIn('successfully verified', message.lower())

            asset.refresh_from_db()
            self.assertEqual(asset.verification_status, Asset.VerificationStatus.VERIFIED)
            self.assertTrue(asset.is_authorized)
            self.assertIsNotNone(asset.authorization_expires_at)

    def test_http_token_verification_success(self):
        asset = Asset.objects.create(
            organization=self.org,
            name='HTTP App',
            domain='http.example.com',
            base_url='https://http.example.com',
            verification_status=Asset.VerificationStatus.PENDING
        )
        challenge = AuthorizationChallenge.objects.create(
            asset=asset,
            challenge_type=AuthorizationChallenge.ChallengeType.HTTP_TOKEN,
            token='http-secret-token-xyz',
            expires_at=timezone.now() + timedelta(days=7)
        )

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = 'http-secret-token-xyz'

        with patch('apps.assets.services.verifier.TargetSafetyValidator.validate_target_safety'), \
             patch('requests.get', return_value=mock_resp):

            success, message = AssetVerificationService.verify_challenge(challenge)
            self.assertTrue(success)

            asset.refresh_from_db()
            self.assertEqual(asset.verification_status, Asset.VerificationStatus.VERIFIED)
            self.assertTrue(asset.is_authorized)

    def test_authorization_expiration_logic(self):
        # Asset verified, but authorization expired yesterday
        asset = Asset.objects.create(
            organization=self.org,
            name='Expired App',
            domain='expired.example.com',
            base_url='https://expired.example.com',
            verification_status=Asset.VerificationStatus.VERIFIED,
            verified_at=timezone.now() - timedelta(days=91),
            authorization_expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(asset.is_authorized)

    def test_ipv6_mapped_ssrf_blocking(self):
        with patch('socket.getaddrinfo', return_value=[(None, None, None, None, ('::ffff:127.0.0.1', 80))]):
            with self.assertRaises(SecurityScopeError) as ctx:
                TargetSafetyValidator.validate_target_safety('malicious-ipv6.com')
            self.assertIn('prohibited loopback address', str(ctx.exception))
