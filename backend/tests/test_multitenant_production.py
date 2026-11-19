import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['USE_SQLITE'] = 'True'
django.setup()

from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership
from apps.assets.models import Asset
from apps.scans.models import Scan
from apps.findings.models import Finding
from apps.reports.models import Report

@override_settings(ALLOW_PRIVATE_IP_SCANS=True)
class MultiTenantIsolationProductionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # =====================================================================
        # Tenant A: Alpha Security
        # =====================================================================
        self.org_a = Organization.objects.create(name="Alpha Security Corp", slug="alpha-sec")
        self.user_a = User.objects.create_user(
            email="admin@alpha.com",
            password="SecureEnterprisePassword2026!",
            role=User.Role.ORG_ADMIN,
            current_organization=self.org_a
        )
        Membership.objects.create(user=self.user_a, organization=self.org_a, role=Membership.OrgRole.ADMIN)

        self.asset_a = Asset.objects.create(
            organization=self.org_a,
            name="Alpha Production App",
            domain="alpha-app.corp",
            base_url="https://alpha-app.corp",
            verification_status=Asset.VerificationStatus.VERIFIED
        )
        self.scan_a = Scan.objects.create(
            organization=self.org_a,
            asset=self.asset_a,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED
        )
        self.finding_a = Finding.objects.create(
            organization=self.org_a,
            scan=self.scan_a,
            asset=self.asset_a,
            title="Alpha SQL Injection Flaw",
            severity="critical"
        )
        self.report_a = Report.objects.create(
            organization=self.org_a,
            scan=self.scan_a,
            report_type=Report.ReportType.TECHNICAL_FULL,
            status=Report.Status.COMPLETED,
            metrics_summary={"critical": 1}
        )

        # =====================================================================
        # Tenant B: Beta Cyber Defense
        # =====================================================================
        self.org_b = Organization.objects.create(name="Beta Cyber Defense", slug="beta-cyber")
        self.user_b = User.objects.create_user(
            email="admin@beta.com",
            password="SecureEnterprisePassword2026!",
            role=User.Role.ORG_ADMIN,
            current_organization=self.org_b
        )
        Membership.objects.create(user=self.user_b, organization=self.org_b, role=Membership.OrgRole.ADMIN)

        self.asset_b = Asset.objects.create(
            organization=self.org_b,
            name="Beta Core Banking API",
            domain="banking.beta-cyber.corp",
            base_url="https://banking.beta-cyber.corp",
            verification_status=Asset.VerificationStatus.VERIFIED
        )
        self.scan_b = Scan.objects.create(
            organization=self.org_b,
            asset=self.asset_b,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED
        )
        self.finding_b = Finding.objects.create(
            organization=self.org_b,
            scan=self.scan_b,
            asset=self.asset_b,
            title="Beta Sensitive PII Data Exposure",
            severity="critical"
        )
        self.report_b = Report.objects.create(
            organization=self.org_b,
            scan=self.scan_b,
            report_type=Report.ReportType.TECHNICAL_FULL,
            status=Report.Status.COMPLETED,
            metrics_summary={"critical": 1}
        )

    # -------------------------------------------------------------------------
    # 1. Direct Object Manipulation (IDOR) Checks
    # -------------------------------------------------------------------------
    def test_tenant_a_cannot_access_tenant_b_asset_by_id(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/assets/{self.asset_b.id}/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_access_tenant_b_scan_by_id(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/scans/{self.scan_b.id}/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_access_tenant_b_finding_by_id(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/findings/{self.finding_b.id}/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_access_tenant_b_report_by_id(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/reports/{self.report_b.id}/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_download_tenant_b_pdf_report(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/reports/{self.report_b.id}/download/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_access_tenant_b_organization_details(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/organizations/{self.org_b.id}/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_tenant_a_cannot_inspect_tenant_b_members(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get(f"/api/v1/organizations/{self.org_b.id}/members/")
        self.assertIn(res.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    # -------------------------------------------------------------------------
    # 2. List Queryset Filtering Isolation
    # -------------------------------------------------------------------------
    def test_tenant_a_asset_list_never_contains_tenant_b_assets(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/assets/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        domains = [item["domain"] for item in res.data.get("results", res.data)]
        self.assertIn(self.asset_a.domain, domains)
        self.assertNotIn(self.asset_b.domain, domains)

    def test_tenant_a_findings_list_never_contains_tenant_b_findings(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/findings/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in res.data.get("results", res.data)]
        self.assertIn(self.finding_a.title, titles)
        self.assertNotIn(self.finding_b.title, titles)

    def test_tenant_a_reports_list_never_contains_tenant_b_reports(self):
        self.client.force_authenticate(user=self.user_a)
        res = self.client.get("/api/v1/reports/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        report_ids = [item["id"] for item in res.data.get("results", res.data)]
        self.assertIn(str(self.report_a.id), report_ids)
        self.assertNotIn(str(self.report_b.id), report_ids)
