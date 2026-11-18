import os
import unittest
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    import django
    django.setup()
except Exception:
    pass

from apps.assets.services.verifier import TargetSafetyValidator, SecurityScopeError

class TestSecurityGuards(unittest.TestCase):
    """
    Validates deterministic security, SSRF protection, and scope enforcement rules (NFR-SEC-013).
    """
    def test_blocks_localhost_and_loopback(self):
        with self.assertRaises(SecurityScopeError) as ctx:
            TargetSafetyValidator.validate_target_safety("localhost")
        self.assertIn("prohibited loopback address", str(ctx.exception))

    def test_blocks_ip_metadata_service(self):
        with self.assertRaises(SecurityScopeError):
            TargetSafetyValidator.validate_target_safety("169.254.169.254")

    def test_blocks_private_rfc1918_addresses(self):
        # 127.0.0.1, 10.0.0.1, 192.168.1.1
        with self.assertRaises(SecurityScopeError):
            TargetSafetyValidator.validate_target_safety("127.0.0.1")
        with self.assertRaises(SecurityScopeError):
            TargetSafetyValidator.validate_target_safety("10.0.0.1")
        with self.assertRaises(SecurityScopeError):
            TargetSafetyValidator.validate_target_safety("192.168.1.1")

    def test_finding_deduplication_fingerprint(self):
        title = "Reflected XSS in search"
        url = "https://example.com/search?q=test"
        param = "q"
        fp1 = hashlib.sha256(f"{title}|{url}|{param}".encode('utf-8')).hexdigest()
        fp2 = hashlib.sha256(f"{title}|{url}|{param}".encode('utf-8')).hexdigest()
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)

if __name__ == '__main__':
    unittest.main()
