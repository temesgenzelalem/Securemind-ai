import logging
import time
import requests
from django.conf import settings
from apps.assets.models import Asset

logger = logging.getLogger(__name__)

class ZAPScannerService:
    """
    Communicates with the OWASP ZAP daemon API to execute spidering,
    passive analysis, and controlled active scanning.
    """
    def __init__(self):
        self.base_url = getattr(settings, 'ZAP_API_URL', 'http://zap:8080').rstrip('/')
        self.api_key = getattr(settings, 'ZAP_API_KEY', 'securemind-zap-api-key')
        self.headers = {'X-ZAP-API-Key': self.api_key}

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/JSON/core/view/version/", headers=self.headers, timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def start_spider(self, target_url: str, max_children: int = 20) -> str:
        """Starts a spidering task against the target URL."""
        params = {
            'apikey': self.api_key,
            'url': target_url,
            'maxChildren': max_children,
            'recurse': 'true'
        }
        resp = requests.get(f"{self.base_url}/JSON/spider/action/scan/", params=params, timeout=10)
        data = resp.json()
        return data.get('scan', '')

    def get_spider_status(self, scan_id: str) -> int:
        """Returns spider progress percentage (0 - 100)."""
        params = {'apikey': self.api_key, 'scanId': scan_id}
        resp = requests.get(f"{self.base_url}/JSON/spider/view/status/", params=params, timeout=10)
        data = resp.json()
        return int(data.get('status', 0))

    def wait_for_passive_scan(self, timeout_seconds: int = 60):
        """Waits until the passive scanner queue has completed analyzing observed responses."""
        start = time.time()
        while time.time() - start < timeout_seconds:
            params = {'apikey': self.api_key}
            resp = requests.get(f"{self.base_url}/JSON/pscan/view/recordsToScan/", params=params, timeout=10)
            data = resp.json()
            records_left = int(data.get('recordsToScan', 0))
            if records_left == 0:
                break
            time.sleep(2)

    def start_active_scan(self, target_url: str, scan_policy: str = 'Default Policy') -> str:
        """Starts a controlled active scan against the target URL."""
        params = {
            'apikey': self.api_key,
            'url': target_url,
            'recurse': 'true',
            'inScopeOnly': 'true',
            'scanPolicyName': scan_policy
        }
        resp = requests.get(f"{self.base_url}/JSON/ascan/action/scan/", params=params, timeout=10)
        data = resp.json()
        return data.get('scan', '')

    def get_active_scan_status(self, scan_id: str) -> int:
        """Returns active scan progress percentage (0 - 100)."""
        params = {'apikey': self.api_key, 'scanId': scan_id}
        resp = requests.get(f"{self.base_url}/JSON/ascan/view/status/", params=params, timeout=10)
        data = resp.json()
        return int(data.get('status', 0))

    def get_alerts(self, base_url: str) -> list[dict]:
        """Retrieves raw alerts reported by ZAP for the target URL."""
        params = {
            'apikey': self.api_key,
            'baseurl': base_url
        }
        resp = requests.get(f"{self.base_url}/JSON/core/view/alerts/", params=params, timeout=15)
        data = resp.json()
        return data.get('alerts', [])
