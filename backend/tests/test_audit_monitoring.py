import uuid
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership
from apps.assets.models import Asset
from apps.scans.models import Scan, ScanSchedule, AssessmentNotification
from apps.findings.models import Finding
from apps.findings.services.normalizer import FindingNormalizerService
from apps.audit.models import AuditLog
from apps.scans.services.comparison import ScanComparisonService
from apps.scans.tasks import run_scheduled_assessments

class AuditMonitoringTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='auditor@securemind.ai',
            password='AuditPassword123!',
            role=User.Role.ORG_ADMIN
        )
        self.org = Organization.objects.create(
            name='Audit Monitoring Corp',
            slug='audit-corp',
            created_by=self.user
        )
        Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.OrgRole.ADMIN
        )
        self.user.current_organization = self.org
        self.user.save(update_fields=['current_organization'])

        self.client.force_authenticate(user=self.user)

        self.asset = Asset.objects.create(
            organization=self.org,
            name='Audit Test App',
            domain='app.auditcorp.local',
            base_url='https://app.auditcorp.local',
            verification_status=Asset.VerificationStatus.VERIFIED,
            authorization_expires_at=timezone.now() + timedelta(days=60)
        )

    def test_audit_trail_recorded_and_filterable(self):
        # 1. Generate audit log events
        AuditLog.objects.create(
            organization=self.org,
            actor=self.user,
            action='asset_created',
            target_type='Asset',
            target_id=str(self.asset.id),
            details={'domain': self.asset.domain}
        )
        AuditLog.objects.create(
            organization=self.org,
            actor=self.user,
            action='scan_created',
            target_type='Scan',
            target_id=str(uuid.uuid4()),
            details={'scan_type': 'passive'}
        )

        # 2. Query audit logs via API
        response = self.client.get('/api/v1/audit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 2)

        # 3. Test filter by action
        filter_resp = self.client.get('/api/v1/audit/?action=scan_created')
        self.assertEqual(filter_resp.status_code, status.HTTP_200_OK)
        filter_results = filter_resp.data.get('results', filter_resp.data)
        for item in filter_results:
            self.assertEqual(item['action'], 'scan_created')

    def test_scan_comparison_and_recurring_vulnerability_diff(self):
        # Scan 1: Baseline Scan with 2 findings
        scan1 = Scan.objects.create(
            asset=self.asset,
            organization=self.org,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED,
            completed_at=timezone.now() - timedelta(days=2)
        )
        fp_sqli = FindingNormalizerService.compute_fingerprint("SQL Injection", "https://app.auditcorp.local/api/users", "id")
        fp_xss = FindingNormalizerService.compute_fingerprint("Reflected XSS", "https://app.auditcorp.local/search", "q")

        f1 = Finding.objects.create(
            scan=scan1,
            asset=self.asset,
            organization=self.org,
            title="SQL Injection",
            severity=Finding.Severity.CRITICAL,
            affected_url="https://app.auditcorp.local/api/users",
            parameter="id",
            fingerprint=fp_sqli
        )
        f2 = Finding.objects.create(
            scan=scan1,
            asset=self.asset,
            organization=self.org,
            title="Reflected XSS",
            severity=Finding.Severity.HIGH,
            affected_url="https://app.auditcorp.local/search",
            parameter="q",
            fingerprint=fp_xss
        )

        # Scan 2: Target Scan where SQLi is fixed, XSS recurs, and Missing CSP is new
        scan2 = Scan.objects.create(
            asset=self.asset,
            organization=self.org,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED,
            completed_at=timezone.now()
        )
        fp_csp = FindingNormalizerService.compute_fingerprint("Missing CSP Header", "https://app.auditcorp.local/", "")

        # Recurring XSS
        Finding.objects.create(
            scan=scan2,
            asset=self.asset,
            organization=self.org,
            title="Reflected XSS",
            severity=Finding.Severity.HIGH,
            affected_url="https://app.auditcorp.local/search",
            parameter="q",
            fingerprint=fp_xss
        )
        # New CSP Finding
        Finding.objects.create(
            scan=scan2,
            asset=self.asset,
            organization=self.org,
            title="Missing CSP Header",
            severity=Finding.Severity.LOW,
            affected_url="https://app.auditcorp.local/",
            parameter="",
            fingerprint=fp_csp
        )

        # Compare via API endpoint
        url = f'/api/v1/scans/{scan2.id}/compare/?with={scan1.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        diff = response.data
        self.assertTrue(diff['has_baseline'])
        summary = diff['summary']
        self.assertEqual(summary['new_count'], 1)  # CSP
        self.assertEqual(summary['resolved_count'], 1)  # SQLi
        self.assertEqual(summary['recurring_count'], 1)  # XSS
        self.assertEqual(summary['net_change'], 0)

        new_titles = [f['title'] for f in diff['new_findings']]
        resolved_titles = [f['title'] for f in diff['resolved_findings']]
        recurring_titles = [f['title'] for f in diff['recurring_findings']]

        self.assertIn("Missing CSP Header", new_titles)
        self.assertIn("SQL Injection", resolved_titles)
        self.assertIn("Reflected XSS", recurring_titles)

    def test_asset_history_progression_endpoint(self):
        Scan.objects.create(
            asset=self.asset,
            organization=self.org,
            scan_type=Scan.ScanType.PASSIVE,
            status=Scan.Status.COMPLETED,
            completed_at=timezone.now()
        )
        url = f'/api/v1/assets/{self.asset.id}/history/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_id'], str(self.asset.id))
        self.assertGreaterEqual(response.data['total_scans'], 1)

    def test_recurring_scan_schedule_management_and_trigger(self):
        # 1. Create schedule via API
        schedule_data = {
            'asset': str(self.asset.id),
            'scan_type': 'passive',
            'frequency': 'weekly'
        }
        create_resp = self.client.post('/api/v1/monitoring/schedules/', schedule_data, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        schedule_id = create_resp.data['id']

        # Set next_run_at in the past so it triggers
        sched = ScanSchedule.objects.get(id=schedule_id)
        sched.next_run_at = timezone.now() - timedelta(minutes=5)
        sched.save(update_fields=['next_run_at'])

        # 2. Execute periodic task
        result = run_scheduled_assessments()
        self.assertIn("Triggered 1 scheduled assessments", result)

        # 3. Verify triggered scan was created
        created_scan = Scan.objects.filter(asset=self.asset).first()
        self.assertIsNotNone(created_scan)
        self.assertIn(created_scan.status, (Scan.Status.QUEUED, Scan.Status.RUNNING, Scan.Status.COMPLETED))

        # 4. Verify notification generated
        notif = AssessmentNotification.objects.filter(
            organization=self.org,
            notification_type=AssessmentNotification.NotificationType.SCHEDULE_TRIGGERED
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn(self.asset.domain, notif.title)

    def test_monitoring_stats_and_notification_read(self):
        # 1. Query Monitoring Stats
        stats_resp = self.client.get('/api/v1/monitoring/stats/')
        self.assertEqual(stats_resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_assets', stats_resp.data)
        self.assertIn('verified_assets', stats_resp.data)
        self.assertIn('findings_summary', stats_resp.data)

        # 2. Create and mark notification as read
        notif = AssessmentNotification.objects.create(
            organization=self.org,
            recipient=self.user,
            title='Critical Alert',
            message='Immediate action required',
            severity=AssessmentNotification.SeverityLevel.CRITICAL
        )
        self.assertFalse(notif.is_read)

        mark_resp = self.client.post(f'/api/v1/monitoring/notifications/{notif.id}/mark_read/')
        self.assertEqual(mark_resp.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
