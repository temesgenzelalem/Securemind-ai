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
from apps.assets.models import Asset
from apps.scans.models import Scan, ScannerExecution
from apps.findings.models import Finding
from apps.scans.tasks import execute_assessment_workflow
from apps.findings.services.normalizer import FindingNormalizerService

class ScannerIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='auditor@example.com',
            password='StrongPassword123!',
            role=User.Role.SECURITY_ANALYST
        )
        self.org = Organization.objects.create(name='Scanner Test Org', slug='scanner-test')
        Membership.objects.create(user=self.user, organization=self.org, role=Membership.OrgRole.SECURITY_ANALYST)
        self.user.current_organization = self.org
        self.user.save()

        # Authorized Asset
        self.authorized_asset = Asset.objects.create(
            organization=self.org,
            name='Test App Target',
            domain='testapp.local',
            base_url='http://test_target:9090',
            verification_status=Asset.VerificationStatus.VERIFIED,
            verified_at=timezone.now(),
            authorization_expires_at=timezone.now() + timedelta(days=90)
        )

        # Unverified Asset
        self.unverified_asset = Asset.objects.create(
            organization=self.org,
            name='Unverified Target',
            domain='unverified.local',
            base_url='http://unverified.local',
            verification_status=Asset.VerificationStatus.PENDING
        )

    def test_unauthorized_asset_scan_aborted(self):
        scan = Scan.objects.create(
            asset=self.unverified_asset,
            organization=self.org,
            created_by=self.user,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.QUEUED
        )

        execute_assessment_workflow(str(scan.id))
        scan.refresh_from_db()

        self.assertEqual(scan.status, Scan.Status.FAILED)
        self.assertIn('Target asset ownership has not been verified', scan.error_message)

    def test_unapproved_intrusive_scan_held_in_review(self):
        scan = Scan.objects.create(
            asset=self.authorized_asset,
            organization=self.org,
            created_by=self.user,
            scan_type=Scan.ScanType.CONTROLLED_ACTIVE,
            requires_approval=True,
            is_approved=False,
            status=Scan.Status.PENDING
        )

        execute_assessment_workflow(str(scan.id))
        scan.refresh_from_db()

        self.assertEqual(scan.status, Scan.Status.AUTHORIZATION_REVIEW)

    def test_finding_normalizer_from_zap_alerts(self):
        scan = Scan.objects.create(
            asset=self.authorized_asset,
            organization=self.org,
            created_by=self.user,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.RUNNING
        )

        sample_zap_alerts = [
            {
                'alert': 'Cross-Domain Misconfiguration',
                'risk': 'Medium',
                'confidence': 'High',
                'url': 'http://test_target:9090/',
                'param': '',
                'cweid': '264',
                'attack': '',
                'evidence': 'Access-Control-Allow-Origin: *',
                'request': 'GET / HTTP/1.1\nHost: test_target:9090',
                'response': 'HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *',
                'description': 'Web server allows cross-domain resource access from arbitrary origins.'
            }
        ]

        findings = FindingNormalizerService.normalize_zap_alerts(scan, sample_zap_alerts)
        self.assertEqual(len(findings), 1)
        finding = findings[0]

        self.assertEqual(finding.title, 'Cross-Domain Misconfiguration')
        self.assertEqual(finding.severity, Finding.Severity.MEDIUM)
        self.assertEqual(finding.cwe_id, 'CWE-264')
        self.assertEqual(finding.source_scanner, 'owasp_zap')
        self.assertEqual(finding.evidences.count(), 1)
        self.assertIn('Access-Control-Allow-Origin', finding.evidences.first().extracted_proof)

    def test_finding_normalizer_from_nuclei_results(self):
        scan = Scan.objects.create(
            asset=self.authorized_asset,
            organization=self.org,
            created_by=self.user,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.RUNNING
        )

        sample_nuclei_results = [
            {
                'template-id': 'http-missing-security-headers',
                'info': {
                    'name': 'Missing Security Headers',
                    'severity': 'low',
                    'description': 'Target does not implement CSP and X-Content-Type-Options headers.',
                    'classification': {
                        'cwe-id': ['CWE-693'],
                        'cvss-score': 3.5
                    }
                },
                'matched-at': 'http://test_target:9090/',
                'request': 'GET / HTTP/1.1\nHost: test_target:9090',
                'response': 'HTTP/1.1 200 OK\nContent-Type: text/html',
                'extracted-results': ['Content-Security-Policy', 'X-Frame-Options']
            }
        ]

        findings = FindingNormalizerService.normalize_nuclei_findings(scan, sample_nuclei_results)
        self.assertEqual(len(findings), 1)
        finding = findings[0]

        self.assertEqual(finding.title, 'Missing Security Headers')
        self.assertEqual(finding.severity, Finding.Severity.LOW)
        self.assertEqual(finding.cwe_id, 'CWE-693')
        self.assertEqual(finding.cvss_score, 3.5)
        self.assertEqual(finding.source_scanner, 'nuclei')
        self.assertEqual(finding.evidences.count(), 1)
