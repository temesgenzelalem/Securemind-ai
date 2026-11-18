import os
import django
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
from apps.scans.models import Scan
from apps.findings.models import Finding
from apps.reports.models import Report

class ReportGenerationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='reporter@example.com',
            password='StrongPassword123!',
            role=User.Role.SECURITY_ANALYST
        )
        self.org = Organization.objects.create(name='Report Org', slug='report-org')
        Membership.objects.create(user=self.user, organization=self.org, role=Membership.OrgRole.ADMIN)
        self.user.current_organization = self.org
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.asset = Asset.objects.create(
            organization=self.org,
            name='Target System',
            domain='report-target.com',
            base_url='https://report-target.com',
            verification_status=Asset.VerificationStatus.VERIFIED,
            authorization_expires_at=timezone.now() + timedelta(days=90)
        )
        self.scan = Scan.objects.create(
            asset=self.asset,
            organization=self.org,
            created_by=self.user,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED
        )

        # Add sample finding
        Finding.objects.create(
            scan=self.scan,
            asset=self.asset,
            organization=self.org,
            title='Sample XSS Finding',
            description='Test description for report',
            severity=Finding.Severity.HIGH,
            verification_status=Finding.VerificationStatus.CONFIRMED,
            affected_url='https://report-target.com/page'
        )

    def test_pdf_report_creation_and_download(self):
        payload = {
            'scan': str(self.scan.id),
            'report_type': Report.ReportType.TECHNICAL_FULL
        }
        response = self.client.post('/api/v1/reports/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Report.Status.COMPLETED)
        self.assertEqual(response.data['metrics_summary']['total_findings'], 1)
        self.assertEqual(response.data['metrics_summary']['high'], 1)

        report_id = response.data['id']
        report = Report.objects.get(id=report_id)
        self.assertTrue(bool(report.pdf_file))

        # Test download endpoint
        dl_resp = self.client.get(f'/api/v1/reports/{report_id}/download/')
        self.assertEqual(dl_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(dl_resp['Content-Type'], 'application/pdf')
        self.assertTrue(dl_resp.content.startswith(b'%PDF-'))
