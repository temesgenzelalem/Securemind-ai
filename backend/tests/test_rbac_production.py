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
from apps.remediation.models import Remediation

@override_settings(ALLOW_PRIVATE_IP_SCANS=True)
class RBACProductionSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Workspace Organization
        self.org = Organization.objects.create(name="Cybersec Corp", slug="cybersec-corp")

        # 1. Platform Admin
        self.platform_admin = User.objects.create_user(
            email="platform.admin@securemind.ai",
            password="SecureEnterprisePassword2026!",
            role=User.Role.PLATFORM_ADMIN,
            current_organization=self.org
        )

        # 2. Org Admin
        self.org_admin = User.objects.create_user(
            email="org.admin@securemind.ai",
            password="SecureEnterprisePassword2026!",
            role=User.Role.ORG_ADMIN,
            current_organization=self.org
        )
        Membership.objects.create(user=self.org_admin, organization=self.org, role=Membership.OrgRole.ADMIN)

        # 3. Security Analyst
        self.analyst = User.objects.create_user(
            email="analyst@securemind.ai",
            password="SecureEnterprisePassword2026!",
            role=User.Role.SECURITY_ANALYST,
            current_organization=self.org
        )
        Membership.objects.create(user=self.analyst, organization=self.org, role=Membership.OrgRole.SECURITY_ANALYST)

        # 4. Developer
        self.developer = User.objects.create_user(
            email="developer@securemind.ai",
            password="SecureEnterprisePassword2026!",
            role=User.Role.DEVELOPER,
            current_organization=self.org
        )
        Membership.objects.create(user=self.developer, organization=self.org, role=Membership.OrgRole.DEVELOPER)

        # 5. Viewer
        self.viewer = User.objects.create_user(
            email="viewer@securemind.ai",
            password="SecureEnterprisePassword2026!",
            role=User.Role.VIEWER,
            current_organization=self.org
        )
        Membership.objects.create(user=self.viewer, organization=self.org, role=Membership.OrgRole.VIEWER)

        # Verified Asset
        self.asset = Asset.objects.create(
            organization=self.org,
            name="Production Portal",
            domain="portal.cybersec.corp",
            base_url="https://portal.cybersec.corp",
            verification_status=Asset.VerificationStatus.VERIFIED
        )

        # Scan
        self.scan = Scan.objects.create(
            organization=self.org,
            asset=self.asset,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED
        )

        # Finding & Remediation
        self.finding = Finding.objects.create(
            organization=self.org,
            scan=self.scan,
            asset=self.asset,
            title="Reflected XSS in Search Query",
            severity="high",
            confidence_score=0.95
        )
        self.remediation = Remediation.objects.create(
            finding=self.finding,
            explanation="Sanitize Search Input via Context-Aware Encoding",
            remediation_strategy="Use HTML escaping on user inputs.",
            status=Remediation.Status.OPEN
        )

    # -------------------------------------------------------------------------
    # 1. Asset Management RBAC
    # -------------------------------------------------------------------------
    def test_viewer_cannot_create_asset(self):
        self.client.force_authenticate(user=self.viewer)
        payload = {"name": "Malicious Asset", "base_url": "https://malicious.org"}
        res = self.client.post("/api/v1/assets/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_cannot_create_asset(self):
        self.client.force_authenticate(user=self.developer)
        payload = {"name": "Dev Asset", "base_url": "https://dev.internal"}
        res = self.client.post("/api/v1/assets/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_create_asset(self):
        self.client.force_authenticate(user=self.analyst)
        payload = {"name": "Staging App", "base_url": "https://staging.cybersec.corp"}
        res = self.client.post("/api/v1/assets/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # -------------------------------------------------------------------------
    # 2. Security Assessment Scan Launch RBAC
    # -------------------------------------------------------------------------
    def test_viewer_cannot_launch_scan(self):
        self.client.force_authenticate(user=self.viewer)
        payload = {"asset": str(self.asset.id), "scan_type": "passive"}
        res = self.client.post("/api/v1/scans/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_cannot_launch_scan(self):
        self.client.force_authenticate(user=self.developer)
        payload = {"asset": str(self.asset.id), "scan_type": "passive"}
        res = self.client.post("/api/v1/scans/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_launch_scan(self):
        self.client.force_authenticate(user=self.analyst)
        payload = {"asset": str(self.asset.id), "scan_type": "passive"}
        res = self.client.post("/api/v1/scans/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # -------------------------------------------------------------------------
    # 3. Remediation Center RBAC
    # -------------------------------------------------------------------------
    def test_viewer_cannot_update_remediation_status(self):
        self.client.force_authenticate(user=self.viewer)
        payload = {"status": "in_progress"}
        res = self.client.patch(f"/api/v1/remediation/{self.remediation.id}/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_developer_can_update_remediation_status(self):
        self.client.force_authenticate(user=self.developer)
        payload = {"status": "in_progress"}
        res = self.client.patch(f"/api/v1/remediation/{self.remediation.id}/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.remediation.refresh_from_db()
        self.assertEqual(self.remediation.status, Remediation.Status.IN_PROGRESS)

    # -------------------------------------------------------------------------
    # 4. Team Member Management RBAC
    # -------------------------------------------------------------------------
    def test_analyst_cannot_invite_team_members(self):
        self.client.force_authenticate(user=self.analyst)
        payload = {"email": "contractor@cybersec.corp", "role": "developer"}
        res = self.client.post(f"/api/v1/organizations/{self.org.id}/members/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_org_admin_can_invite_team_members(self):
        # Create user to invite
        User.objects.create_user(email="newhire@cybersec.corp", password="Password123!", role=User.Role.DEVELOPER)
        self.client.force_authenticate(user=self.org_admin)
        payload = {"email": "newhire@cybersec.corp", "role": "developer"}
        res = self.client.post(f"/api/v1/organizations/{self.org.id}/members/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # -------------------------------------------------------------------------
    # 5. Privilege Escalation Prevention
    # -------------------------------------------------------------------------
    def test_public_registration_cannot_claim_platform_admin(self):
        payload = {
            "email": "attacker@evil.com",
            "password": "StrongPassword2026!",
            "role": "platform_admin",
            "first_name": "Bad",
            "last_name": "Actor"
        }
        res = self.client.post("/api/v1/auth/register/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", res.data)

    def test_user_cannot_escalate_own_role_via_profile_patch(self):
        self.client.force_authenticate(user=self.developer)
        payload = {"role": "platform_admin"}
        res = self.client.patch("/api/v1/auth/me/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.developer.refresh_from_db()
        # Role must remain developer
        self.assertEqual(self.developer.role, User.Role.DEVELOPER)

    # -------------------------------------------------------------------------
    # 6. JWT Token Blacklisting & Logout
    # -------------------------------------------------------------------------
    def test_logout_blacklists_refresh_token(self):
        login_res = self.client.post("/api/v1/auth/login/", {
            "email": "developer@securemind.ai",
            "password": "SecureEnterprisePassword2026!"
        }, format="json")
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        access = login_res.data["access"]
        refresh = login_res.data["refresh"]

        # Authenticate and call logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_res = self.client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json")
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)

        # Attempt to use blacklisted refresh token
        refresh_res = self.client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)
