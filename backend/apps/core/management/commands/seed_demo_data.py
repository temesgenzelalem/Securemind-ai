from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership
from apps.assets.models import Asset, ScopeRule
from apps.scans.models import Scan, ScannerExecution, ScanSchedule, AssessmentNotification
from apps.findings.models import Finding, Evidence
from apps.findings.services.normalizer import FindingNormalizerService
from apps.remediation.models import Remediation
from apps.audit.models import AuditLog
from apps.orchestrator.models import AgentExecution, WorkflowState

class Command(BaseCommand):
    help = 'Seeds initial demonstration data for SecureMind AI presentation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing demo data for SecureMind AI..."))

        # 1. Administrator User
        user, created = User.objects.get_or_create(
            email='admin@securemind.ai',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Vance',
                'role': User.Role.PLATFORM_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        user.set_password('SecureEnterprisePassword2026!')
        user.save()

        # 2. Organization Administrator User
        org_admin_user, _ = User.objects.get_or_create(
            email='orgadmin@securemind.ai',
            defaults={
                'first_name': 'Morgan',
                'last_name': 'Reed',
                'role': User.Role.ORG_ADMIN,
            }
        )
        org_admin_user.set_password('SecureEnterprisePassword2026!')
        org_admin_user.save()

        # 3. Security Analyst User
        analyst_user, _ = User.objects.get_or_create(
            email='analyst@securemind.ai',
            defaults={
                'first_name': 'Elena',
                'last_name': 'Rostova',
                'role': User.Role.SECURITY_ANALYST,
            }
        )
        analyst_user.set_password('SecureEnterprisePassword2026!')
        analyst_user.save()

        # 4. Developer User
        dev_user, _ = User.objects.get_or_create(
            email='dev@securemind.ai',
            defaults={
                'first_name': 'Sam',
                'last_name': 'Taylor',
                'role': User.Role.DEVELOPER,
            }
        )
        dev_user.set_password('SecureEnterprisePassword2026!')
        dev_user.save()

        # 5. Viewer User
        viewer_user, _ = User.objects.get_or_create(
            email='viewer@securemind.ai',
            defaults={
                'first_name': 'Jordan',
                'last_name': 'Lee',
                'role': User.Role.VIEWER,
            }
        )
        viewer_user.set_password('SecureEnterprisePassword2026!')
        viewer_user.save()

        # 6. Organization
        org, _ = Organization.objects.get_or_create(
            slug='acme-cyber-defense',
            defaults={
                'name': 'Acme Cyber Defense',
                'created_by': user,
            }
        )

        Membership.objects.get_or_create(user=user, organization=org, defaults={'role': Membership.OrgRole.ADMIN})
        Membership.objects.get_or_create(user=org_admin_user, organization=org, defaults={'role': Membership.OrgRole.ADMIN})
        Membership.objects.get_or_create(user=analyst_user, organization=org, defaults={'role': Membership.OrgRole.MEMBER})
        Membership.objects.get_or_create(user=dev_user, organization=org, defaults={'role': Membership.OrgRole.MEMBER})
        Membership.objects.get_or_create(user=viewer_user, organization=org, defaults={'role': Membership.OrgRole.MEMBER})

        for u in [user, org_admin_user, analyst_user, dev_user, viewer_user]:
            u.current_organization = org
            u.save(update_fields=['current_organization'])

        # 3. Verified Practice Asset
        practice_asset, _ = Asset.objects.get_or_create(
            organization=org,
            domain='localhost:9090',
            defaults={
                'name': 'SecureMind Practice Target (Port 9090)',
                'base_url': 'http://localhost:9090',
                'verification_status': Asset.VerificationStatus.VERIFIED,
                'verified_at': timezone.now() - timedelta(days=10),
                'authorization_expires_at': timezone.now() + timedelta(days=80),
                'is_active': True,
            }
        )

        # Production Web Asset
        prod_asset, _ = Asset.objects.get_or_create(
            organization=org,
            domain='portal.acme.corp',
            defaults={
                'name': 'Production Customer Portal',
                'base_url': 'https://portal.acme.corp',
                'verification_status': Asset.VerificationStatus.VERIFIED,
                'verified_at': timezone.now() - timedelta(days=5),
                'authorization_expires_at': timezone.now() + timedelta(days=85),
                'is_active': True,
            }
        )

        ScopeRule.objects.get_or_create(
            asset=practice_asset,
            pattern='/admin/logout',
            defaults={'rule_type': ScopeRule.RuleType.EXCLUDE}
        )

        # 4. Completed Scan with Findings & Evidence
        completed_scan = Scan.objects.filter(
            asset=practice_asset,
            organization=org,
            scan_type=Scan.ScanType.CONTROLLED_ACTIVE,
            status=Scan.Status.COMPLETED
        ).first()

        if not completed_scan:
            completed_scan = Scan.objects.create(
                asset=practice_asset,
                organization=org,
                scan_type=Scan.ScanType.CONTROLLED_ACTIVE,
                status=Scan.Status.COMPLETED,
                is_approved=True,
                approved_by=user,
                created_by=user,
                started_at=timezone.now() - timedelta(hours=2),
                completed_at=timezone.now() - timedelta(hours=1, minutes=45),
            )

        ScannerExecution.objects.get_or_create(
            scan=completed_scan,
            scanner_type=ScannerExecution.ScannerType.OWASP_ZAP,
            defaults={
                'status': ScannerExecution.ExecutionStatus.COMPLETED,
                'raw_output': {'alerts_count': 3, 'spider_urls_count': 6},
                'execution_stats': {'duration_seconds': 14.2}
            }
        )

        ScannerExecution.objects.get_or_create(
            scan=completed_scan,
            scanner_type=ScannerExecution.ScannerType.NUCLEI,
            defaults={
                'status': ScannerExecution.ExecutionStatus.COMPLETED,
                'raw_output': {'templates_matched': 2},
                'execution_stats': {'duration_seconds': 6.8}
            }
        )

        # Finding 1: Reflected XSS
        fp_xss = FindingNormalizerService.compute_fingerprint(
            "Reflected Cross-Site Scripting (XSS)", "http://localhost:9090/search", "q"
        )
        f_xss, _ = Finding.objects.get_or_create(
            scan=completed_scan,
            fingerprint=fp_xss,
            defaults={
                'asset': practice_asset,
                'organization': org,
                'title': "Reflected Cross-Site Scripting (XSS)",
                'description': "The search query parameter 'q' is reflected in the HTML response without HTML entity encoding, permitting execution of arbitrary JavaScript.",
                'vulnerability_category': 'Cross-Site Scripting',
                'cwe_id': 'CWE-79',
                'cvss_score': 7.5,
                'cvss_vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N',
                'severity': Finding.Severity.HIGH,
                'verification_status': Finding.VerificationStatus.CONFIRMED,
                'confidence_score': 0.95,
                'source_scanner': 'owasp_zap',
                'affected_url': 'http://localhost:9090/search',
                'http_method': 'GET',
                'parameter': 'q',
            }
        )

        Evidence.objects.get_or_create(
            finding=f_xss,
            evidence_type=Evidence.EvidenceType.RESPONSE_REFLECTION,
            defaults={
                'raw_http_request': "GET /search?q=%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1\nHost: localhost:9090\nUser-Agent: SecureMind-Scanner/1.0",
                'raw_http_response': "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<p>Results for query: <script>alert(1)</script></p>",
                'payload_used': "<script>alert(1)</script>",
                'extracted_proof': "<script>alert(1)</script>",
                'verification_notes': "Payload reflection observed verbatim in unescaped DOM container."
            }
        )

        Remediation.objects.get_or_create(
            finding=f_xss,
            defaults={
                'status': Remediation.Status.OPEN,
                'explanation': "The application takes untrusted user input from the 'q' query parameter and renders it directly into the HTML body. Attackers can execute arbitrary scripts in the victim's browser context.",
                'remediation_strategy': "Apply contextual HTML entity escaping before rendering user values, and configure a strict Content-Security-Policy (CSP) header.",
                'code_snippets': [
                    {
                        'language': 'Python',
                        'framework': 'Django / Standard Library',
                        'before_code': 'html = f"<p>Results: {query}</p>"',
                        'after_code': 'from html import escape\nhtml = f"<p>Results: {escape(query)}</p>"',
                        'explanation': 'Use standard library escape() or Django template engine auto-escaping.'
                    }
                ],
                'references': ['https://owasp.org/www-community/attacks/xss/', 'https://cwe.mitre.org/data/definitions/79.html']
            }
        )

        # Finding 2: Missing CSP Header
        fp_csp = FindingNormalizerService.compute_fingerprint(
            "Missing Content-Security-Policy (CSP) Header", "http://localhost:9090/", ""
        )
        f_csp, _ = Finding.objects.get_or_create(
            scan=completed_scan,
            fingerprint=fp_csp,
            defaults={
                'asset': practice_asset,
                'organization': org,
                'title': "Missing Content-Security-Policy (CSP) Header",
                'description': "The web application does not specify a Content-Security-Policy response header, increasing exposure to cross-site scripting and data injection attacks.",
                'vulnerability_category': 'Security Header Misconfiguration',
                'cwe_id': 'CWE-1021',
                'cvss_score': 5.3,
                'severity': Finding.Severity.MEDIUM,
                'verification_status': Finding.VerificationStatus.CONFIRMED,
                'confidence_score': 0.90,
                'source_scanner': 'nuclei',
                'affected_url': 'http://localhost:9090/',
                'http_method': 'GET',
                'parameter': '',
            }
        )

        Evidence.objects.get_or_create(
            finding=f_csp,
            evidence_type=Evidence.EvidenceType.HEADER_MISCONFIGURATION,
            defaults={
                'raw_http_request': "GET / HTTP/1.1\nHost: localhost:9090",
                'raw_http_response': "HTTP/1.1 200 OK\nServer: SecureMind-TrainingApp/1.0\nContent-Type: text/html",
                'payload_used': "N/A",
                'extracted_proof': "Headers examined: ['server', 'content-type']. Content-Security-Policy header is absent.",
                'verification_notes': "Missing mandatory browser security header."
            }
        )

        # 5. Pending Scan in Authorization Review (Demonstrates Human-in-the-Loop)
        if not Scan.objects.filter(asset=practice_asset, organization=org, scan_type=Scan.ScanType.COMPREHENSIVE).exists():
            Scan.objects.create(
                asset=practice_asset,
                organization=org,
                scan_type=Scan.ScanType.COMPREHENSIVE,
                status=Scan.Status.AUTHORIZATION_REVIEW,
                requires_approval=True,
                is_approved=False,
                created_by=user,
            )

        # 6. Recurring Schedule
        if not ScanSchedule.objects.filter(asset=practice_asset, organization=org).exists():
            ScanSchedule.objects.create(
                asset=practice_asset,
                organization=org,
                scan_type=Scan.ScanType.PASSIVE,
                frequency=ScanSchedule.Frequency.WEEKLY,
                created_by=user,
                is_active=True,
                next_run_at=timezone.now() + timedelta(days=6)
            )

        # 7. Notifications
        if not AssessmentNotification.objects.filter(organization=org, recipient=user, title='Security Assessment Completed: localhost:9090').exists():
            AssessmentNotification.objects.create(
                organization=org,
                recipient=user,
                title='Security Assessment Completed: localhost:9090',
                notification_type=AssessmentNotification.NotificationType.SCAN_COMPLETED,
                message='Controlled active assessment finished with 2 confirmed findings.',
                severity=AssessmentNotification.SeverityLevel.INFO,
                scan=completed_scan,
                is_read=False
            )

        if not AssessmentNotification.objects.filter(organization=org, recipient=user, title='High/Critical Vulnerabilities Detected on localhost:9090').exists():
            AssessmentNotification.objects.create(
                organization=org,
                recipient=user,
                title='High/Critical Vulnerabilities Detected on localhost:9090',
                notification_type=AssessmentNotification.NotificationType.CRITICAL_FINDING,
                message='Discovered High severity Reflected XSS requiring immediate remediation.',
                severity=AssessmentNotification.SeverityLevel.CRITICAL,
                scan=completed_scan,
                is_read=False
            )

        # 8. Audit Log entries
        if not AuditLog.objects.filter(organization=org, actor=user, action='asset_created', target_id=str(practice_asset.id)).exists():
            AuditLog.objects.create(
                organization=org,
                actor=user,
                action='asset_created',
                target_type='Asset',
                target_id=str(practice_asset.id),
                details={'domain': practice_asset.domain}
            )

        if not AuditLog.objects.filter(organization=org, actor=user, action='scan_completed', target_id=str(completed_scan.id)).exists():
            AuditLog.objects.create(
                organization=org,
                actor=user,
                action='scan_completed',
                target_type='Scan',
                target_id=str(completed_scan.id),
                details={'total_findings': 2, 'scan_type': 'controlled_active'}
            )

        self.stdout.write(self.style.SUCCESS("Demo data successfully seeded for all 5 RBAC roles!"))
        self.stdout.write(self.style.SUCCESS("All demo accounts share password: SecureEnterprisePassword2026!"))
        self.stdout.write(self.style.SUCCESS("- Platform Admin: admin@securemind.ai"))
        self.stdout.write(self.style.SUCCESS("- Org Admin: orgadmin@securemind.ai"))
        self.stdout.write(self.style.SUCCESS("- Security Analyst: analyst@securemind.ai"))
        self.stdout.write(self.style.SUCCESS("- Developer: dev@securemind.ai"))
        self.stdout.write(self.style.SUCCESS("- Viewer: viewer@securemind.ai"))
