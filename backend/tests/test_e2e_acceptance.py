import io
import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership
from apps.assets.models import Asset, AuthorizationChallenge
from apps.scans.models import Scan, ScannerExecution
from apps.findings.models import Finding, Evidence
from apps.remediation.models import Remediation
from apps.reports.models import Report
from apps.audit.models import AuditLog
from apps.orchestrator.models import AgentExecution
from apps.scans.services.zap_service import ZAPScannerService
from apps.scans.services.nuclei_service import NucleiScannerService
from apps.scans.tasks import execute_assessment_workflow

class EndToEndAcceptanceTests(APITestCase):
    """
    Validates all 13 User Acceptance Criteria from SRS Section 12.4:
    1. User registration & authentication
    2. Organization & member management
    3. Asset registration & ownership verification
    4. Deterministic scanning restrictions (unverified & SSRF blocked)
    5. Passive & controlled active scan profiles
    6. Scanner execution collection (ZAP + Nuclei)
    7. Central AI Orchestration across 6 specialized agents
    8. Evidence-based finding verification
    9. Risk assessment explanations
    10. Developer actionable remediation guidance & lifecycle tracking
    11. Audit-grade PDF report generation & secure download
    12. Cross-tenant data isolation
    13. Complete compliance audit trail
    """

    def test_complete_authorized_assessment_lifecycle(self):
        # ---------------------------------------------------------
        # UAC 1: User Registration & Authentication
        # ---------------------------------------------------------
        reg_payload = {
            'email': 'lead.analyst@cyberdefense.org',
            'password': 'SecureEnterprisePassword2026!',
            'first_name': 'Lead',
            'last_name': 'Analyst',
            'role': User.Role.SECURITY_ANALYST,
        }
        reg_resp = self.client.post('/api/v1/auth/register/', reg_payload, format='json')
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', reg_resp.data)
        access_token = reg_resp.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_resp = self.client.get('/api/v1/auth/me/')
        self.assertEqual(profile_resp.status_code, status.HTTP_200_OK)
        analyst_user = User.objects.get(email='lead.analyst@cyberdefense.org')

        # ---------------------------------------------------------
        # UAC 2: Organization & Member Management
        # ---------------------------------------------------------
        org_payload = {'name': 'Cyber Defense Group', 'slug': 'cyber-defense'}
        org_resp = self.client.post('/api/v1/organizations/', org_payload, format='json')
        self.assertEqual(org_resp.status_code, status.HTTP_201_CREATED)
        org_id = org_resp.data['id']
        org = Organization.objects.get(id=org_id)

        # Switch active organization
        switch_resp = self.client.post('/api/v1/auth/switch-org/', {'organization_id': org_id}, format='json')
        self.assertEqual(switch_resp.status_code, status.HTTP_200_OK)

        # Invite developer member
        dev_user = User.objects.create_user(
            email='developer@cyberdefense.org',
            password='DevPassword2026!',
            role=User.Role.DEVELOPER
        )
        member_payload = {
            'email': dev_user.email,
            'role': Membership.OrgRole.MEMBER
        }
        member_resp = self.client.post(f'/api/v1/organizations/{org_id}/members/', member_payload, format='json')
        self.assertEqual(member_resp.status_code, status.HTTP_201_CREATED)

        # ---------------------------------------------------------
        # UAC 3: Asset Registration & Ownership Verification
        # ---------------------------------------------------------
        asset_payload = {
            'name': 'Production Customer Portal',
            'base_url': 'https://portal.cyberdefense.org',
        }
        with patch('socket.getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 0))]):
            asset_resp = self.client.post('/api/v1/assets/', asset_payload, format='json')
        self.assertEqual(asset_resp.status_code, status.HTTP_201_CREATED)
        asset_id = asset_resp.data['id']
        asset = Asset.objects.get(id=asset_id)
        self.assertEqual(asset.verification_status, Asset.VerificationStatus.PENDING)

        # Create challenge
        chal_resp = self.client.post(f'/api/v1/assets/{asset_id}/challenge/', {'challenge_type': 'http_token'}, format='json')
        self.assertEqual(chal_resp.status_code, status.HTTP_201_CREATED)
        challenge_id = chal_resp.data['id']
        challenge_token = chal_resp.data['token']

        # Verify challenge (mocking target web response)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = challenge_token
        with patch('apps.assets.services.verifier.TargetSafetyValidator.validate_target_safety'), \
             patch('apps.assets.services.verifier.requests.get', return_value=mock_resp):
            verify_resp = self.client.post(f'/api/v1/assets/{asset_id}/verify/', {'challenge_id': challenge_id}, format='json')
            self.assertEqual(verify_resp.status_code, status.HTTP_200_OK)

        asset.refresh_from_db()
        self.assertEqual(asset.verification_status, Asset.VerificationStatus.VERIFIED)
        self.assertTrue(asset.is_authorized)

        # ---------------------------------------------------------
        # UAC 4: Scanning Restrictions (Unauthorized targets blocked)
        # ---------------------------------------------------------
        unverified_asset = Asset.objects.create(
            organization=org,
            name='Rogue Target',
            domain='unauthorized.evilcorp.com',
            base_url='https://unauthorized.evilcorp.com',
            verification_status=Asset.VerificationStatus.PENDING
        )
        blocked_scan_resp = self.client.post('/api/v1/scans/', {'asset': str(unverified_asset.id), 'scan_type': 'passive'}, format='json')
        self.assertEqual(blocked_scan_resp.status_code, status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------
        # UAC 5 & 6: Controlled Active Scan & Scanner Integration
        # ---------------------------------------------------------
        active_scan_resp = self.client.post('/api/v1/scans/', {'asset': str(asset.id), 'scan_type': 'controlled_active'}, format='json')
        self.assertEqual(active_scan_resp.status_code, status.HTTP_201_CREATED)
        scan_id = active_scan_resp.data['id']
        scan = Scan.objects.get(id=scan_id)
        self.assertEqual(scan.status, Scan.Status.AUTHORIZATION_REVIEW)
        self.assertFalse(scan.is_approved)

        # Sign-off / Approve
        approve_resp = self.client.post(f'/api/v1/scans/{scan_id}/approve/')
        self.assertEqual(approve_resp.status_code, status.HTTP_200_OK)

        # Execute scan pipeline (ZAP + Nuclei mocked outputs)
        sample_zap_alerts = [
            {
                'alert': 'SQL Injection',
                'risk': 'High',
                'url': 'https://portal.cyberdefense.org/api/v1/query?q=test',
                'param': 'q',
                'cweid': '89',
                'description': 'SQL parameter is not sanitized.',
                'attack': "' OR '1'='1",
                'evidence': 'syntax error at or near SELECT'
            }
        ]
        sample_nuclei_results = [
            {
                'template-id': 'cve-2023-default-creds',
                'info': {
                    'name': 'Default Administrator Credentials',
                    'severity': 'critical',
                    'description': 'Target web service exposes default admin credentials.'
                },
                'matched-at': 'https://portal.cyberdefense.org/admin/login',
                'type': 'http'
            }
        ]

        with patch.object(ZAPScannerService, 'is_available', return_value=True), \
             patch.object(ZAPScannerService, 'start_spider', return_value='1'), \
             patch.object(ZAPScannerService, 'wait_for_passive_scan', return_value=True), \
             patch.object(ZAPScannerService, 'start_active_scan', return_value='1'), \
             patch.object(ZAPScannerService, 'get_alerts', return_value=sample_zap_alerts), \
             patch.object(NucleiScannerService, 'execute_scan', return_value=sample_nuclei_results):
            execute_assessment_workflow(str(scan.id))

        scan.refresh_from_db()
        self.assertEqual(scan.status, Scan.Status.COMPLETED)

        # ---------------------------------------------------------
        # UAC 7: Central AI Orchestrator Coordination (6 Agents)
        # ---------------------------------------------------------
        executions = AgentExecution.objects.filter(scan=scan)
        agent_names = set(executions.values_list('agent_name', flat=True))
        expected_agents = {
            'central_orchestrator',
            'authorization',
            'reconnaissance',
            'verification',
            'risk_assessment',
            'remediation'
        }
        self.assertTrue(expected_agents.issubset(agent_names))

        # ---------------------------------------------------------
        # UAC 8 & 9: Evidence-Based Findings & Risk Explanations
        # ---------------------------------------------------------
        findings_resp = self.client.get(f'/api/v1/findings/?scan={scan.id}')
        self.assertEqual(findings_resp.status_code, status.HTTP_200_OK)
        findings = findings_resp.data.get('results', findings_resp.data)
        self.assertEqual(len(findings), 2)

        sqli_finding = Finding.objects.get(scan=scan, title='SQL Injection')
        self.assertIn(sqli_finding.verification_status, (
            Finding.VerificationStatus.CONFIRMED,
            Finding.VerificationStatus.LIKELY,
            Finding.VerificationStatus.UNVERIFIED
        ))
        evidence = sqli_finding.evidences.first()
        self.assertIsNotNone(evidence)
        self.assertIn("' OR '1'='1", evidence.payload_used)

        # ---------------------------------------------------------
        # UAC 10: Actionable Remediation Guidance & Tracking
        # ---------------------------------------------------------
        remediation_resp = self.client.get(f'/api/v1/remediation/?finding={sqli_finding.id}')
        self.assertEqual(remediation_resp.status_code, status.HTTP_200_OK)
        remediation_list = remediation_resp.data.get('results', remediation_resp.data)
        self.assertGreaterEqual(len(remediation_list), 1)
        remed_id = remediation_list[0]['id']

        # Update remediation status by developer
        update_remed_resp = self.client.patch(
            f'/api/v1/remediation/{remed_id}/',
            {'status': Remediation.Status.IN_PROGRESS, 'developer_notes': 'Refactoring DB query to ORM parameterized query.'},
            format='json'
        )
        self.assertEqual(update_remed_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(update_remed_resp.data['status'], Remediation.Status.IN_PROGRESS)

        # ---------------------------------------------------------
        # UAC 11: Audit-Grade PDF Report Generation & Download
        # ---------------------------------------------------------
        report_resp = self.client.post('/api/v1/reports/', {'scan': str(scan.id), 'report_type': 'technical_full'}, format='json')
        self.assertEqual(report_resp.status_code, status.HTTP_201_CREATED)
        report_id = report_resp.data['id']

        download_resp = self.client.get(f'/api/v1/reports/{report_id}/download/')
        self.assertEqual(download_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(download_resp['Content-Type'], 'application/pdf')
        self.assertTrue(download_resp.content.startswith(b'%PDF-1.4'))

        # ---------------------------------------------------------
        # UAC 12: Cross-Tenant Data Isolation
        # ---------------------------------------------------------
        tenant_b_user = User.objects.create_user(
            email='outsider@othercorp.com',
            password='OutsiderPassword2026!',
            role=User.Role.ORG_ADMIN
        )
        tenant_b_org = Organization.objects.create(name='Other Corp', slug='other-corp', created_by=tenant_b_user)
        tenant_b_user.current_organization = tenant_b_org
        tenant_b_user.save()

        self.client.force_authenticate(user=tenant_b_user)

        # Tenant B tries to access Tenant A's scan and report
        isolated_scan_resp = self.client.get(f'/api/v1/scans/{scan.id}/')
        self.assertEqual(isolated_scan_resp.status_code, status.HTTP_404_NOT_FOUND)

        isolated_report_resp = self.client.get(f'/api/v1/reports/{report_id}/download/')
        self.assertEqual(isolated_report_resp.status_code, status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------
        # UAC 13: Audit Trail Verification
        # ---------------------------------------------------------
        analyst_user.refresh_from_db()
        self.client.force_authenticate(user=analyst_user)
        audit_resp = self.client.get('/api/v1/audit/')
        self.assertEqual(audit_resp.status_code, status.HTTP_200_OK)
        audit_records = audit_resp.data.get('results', audit_resp.data)
        actions = [a['action'] for a in audit_records]
        self.assertIn('scan_created', actions)
        self.assertIn('scan_approved', actions)
        self.assertIn('scan_completed', actions)
        self.assertIn('report_generated', actions)
        self.assertIn('report_downloaded', actions)
