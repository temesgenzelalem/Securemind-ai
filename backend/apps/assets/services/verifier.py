import ipaddress
import socket
import logging
from datetime import timedelta

try:
    import requests
except ImportError:
    requests = None

try:
    from django.utils import timezone
    from django.conf import settings
    from apps.assets.models import Asset, AuthorizationChallenge
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    timezone = None
    settings = None
    Asset = None
    AuthorizationChallenge = None

try:
    import dns.resolver
    import dns.exception
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SecurityScopeError(Exception):
    """Raised when target violates security or SSRF policies."""
    pass

class TargetSafetyValidator:
    """
    Deterministic SSRF and Private IP destination validator.
    Ensures scanners never probe prohibited internal infrastructure.
    """
    @staticmethod
    def validate_target_safety(domain: str) -> None:
        if settings and getattr(settings, 'ALLOW_PRIVATE_IP_SCANS', False):
            return  # Allowed for specific self-hosted enterprise internal testing

        try:
            # Resolve all IPv4 and IPv6 addresses for the hostname
            addr_info = socket.getaddrinfo(domain, None)
            resolved_ips = {item[4][0] for item in addr_info}
        except socket.gaierror as e:
            raise SecurityScopeError(f"Target domain '{domain}' cannot be resolved: {str(e)}")

        for ip_str in resolved_ips:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_loopback:
                raise SecurityScopeError(f"Target '{domain}' resolves to prohibited loopback address ({ip_str}).")
            if ip.is_private:
                raise SecurityScopeError(f"Target '{domain}' resolves to prohibited private network address ({ip_str}). SSRF protection active.")
            if ip.is_link_local:
                raise SecurityScopeError(f"Target '{domain}' resolves to link-local address ({ip_str}).")
            if ip.is_reserved or ip.is_multicast:
                raise SecurityScopeError(f"Target '{domain}' resolves to reserved/multicast address ({ip_str}).")
            # AWS / GCP / Azure Cloud Metadata Service
            if str(ip) == "169.254.169.254":
                raise SecurityScopeError(f"Target '{domain}' resolves to cloud instance metadata endpoint ({ip_str}).")

class AssetVerificationService:
    """
    Executes DNS-based or HTTP-based domain ownership verification.
    """
    @staticmethod
    def verify_challenge(challenge: AuthorizationChallenge) -> tuple[bool, str]:
        asset = challenge.asset
        challenge.last_attempt_at = timezone.now()

        # Check expiration
        if challenge.expires_at < timezone.now():
            challenge.last_attempt_error = "Challenge token has expired. Please generate a new one."
            challenge.save(update_fields=['last_attempt_at', 'last_attempt_error'])
            return False, challenge.last_attempt_error

        # Pre-flight SSRF check
        try:
            TargetSafetyValidator.validate_target_safety(asset.domain)
        except SecurityScopeError as e:
            challenge.last_attempt_error = str(e)
            challenge.save(update_fields=['last_attempt_at', 'last_attempt_error'])
            return False, str(e)

        if challenge.challenge_type == AuthorizationChallenge.ChallengeType.DNS_TXT:
            return AssetVerificationService._verify_dns(challenge)
        elif challenge.challenge_type == AuthorizationChallenge.ChallengeType.HTTP_TOKEN:
            return AssetVerificationService._verify_http(challenge)
        else:
            return False, "Unknown challenge type."

    @staticmethod
    def _verify_dns(challenge: AuthorizationChallenge) -> tuple[bool, str]:
        if not DNS_AVAILABLE:
            return False, "DNS resolution engine (dnspython) is unavailable in current runtime."

        asset = challenge.asset
        expected_token = f"securemind-verify={challenge.token}"
        
        # We check both the domain directly and _securemind-challenge subdomain
        domains_to_check = [
            f"_securemind-challenge.{asset.domain}",
            asset.domain
        ]

        found_records = []
        for domain in domains_to_check:
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                for rdata in answers:
                    for txt_string in rdata.strings:
                        decoded = txt_string.decode('utf-8', errors='ignore')
                        found_records.append(decoded)
                        if expected_token in decoded or challenge.token in decoded:
                            return AssetVerificationService._mark_verified(challenge)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
                continue
            except Exception as e:
                logger.warning(f"DNS query error for {domain}: {e}")

        error_msg = f"Expected TXT record containing '{expected_token}' not found on {asset.domain}."
        if found_records:
            error_msg += f" Found existing TXT records: {', '.join(found_records[:3])}"
        
        challenge.last_attempt_error = error_msg
        challenge.save(update_fields=['last_attempt_at', 'last_attempt_error'])
        return False, error_msg

    @staticmethod
    def _verify_http(challenge: AuthorizationChallenge) -> tuple[bool, str]:
        asset = challenge.asset
        url = f"{asset.base_url.rstrip('/')}{challenge.verification_path}"
        expected_token = challenge.token.strip()

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'SecureMind-AI-Verifier/1.0'},
                allow_redirects=True
            )
            content = response.text.strip()
            if response.status_code == 200 and expected_token in content:
                return AssetVerificationService._mark_verified(challenge)
            else:
                error_msg = f"HTTP challenge failed. URL '{url}' responded with status {response.status_code}. Content does not match token."
        except requests.RequestException as e:
            error_msg = f"Failed to fetch HTTP verification file at '{url}': {str(e)}"

        challenge.last_attempt_error = error_msg
        challenge.save(update_fields=['last_attempt_at', 'last_attempt_error'])
        return False, error_msg

    @staticmethod
    def _mark_verified(challenge: AuthorizationChallenge) -> tuple[bool, str]:
        now = timezone.now()
        challenge.is_verified = True
        challenge.verified_at = now
        challenge.last_attempt_error = ""
        challenge.save(update_fields=['is_verified', 'verified_at', 'last_attempt_at', 'last_attempt_error'])

        # Update Asset status and grant 90-day authorization
        asset = challenge.asset
        asset.verification_status = Asset.VerificationStatus.VERIFIED
        asset.verified_at = now
        asset.authorization_expires_at = now + timedelta(days=90)
        asset.save(update_fields=['verification_status', 'verified_at', 'authorization_expires_at'])

        return True, "Asset ownership successfully verified! Authorization valid for 90 days."
